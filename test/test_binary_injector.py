import subprocess
from pathlib import Path
from typing import List

import pytest

from makka_pakka.elf_caver.exceptions.exceptions import (
    MKPKInvalidParameter,
)
from makka_pakka.elf_caver.injector.binary_injector import (
    _get_shellcode_from_nasm,
)
from makka_pakka.elf_caver.injector.binary_injector import (
    _inject_shellcode_at_offset,
)
from makka_pakka.elf_caver.injector.binary_injector import (
    change_entrypoint,
)
from makka_pakka.elf_caver.injector.binary_injector import (
    inject_nasm_into_binary,
)
from makka_pakka.elf_caver.injector.binary_injector import (
    patch_pltsec_exit,
)
from makka_pakka.elf_caver.injector.byte_extraction import (
    to_little_endian_32bit,
)

RES_PATH: str = Path("test/resources/elf_caver")
HELLO_WORLD_ASM: str = str(RES_PATH / "hello_world.asm")
CRONTAB_BIN: str = str(RES_PATH / "crontab")
CPP_BIN: str = str(RES_PATH / "cpp")
CAT_BIN: str = str(RES_PATH / "cat")


class TestInjectNasmIntoBinary:
    def test_invalid_parameters(self):
        mock_nasm_file = HELLO_WORLD_ASM
        mock_target_file = CPP_BIN
        mock_output_file = "/tmp/cpp_copy"

        try:
            inject_nasm_into_binary(None, None, None)
            pytest.fail(
                "inject_nasm_into_binary should have failed with invalid parameter but\
                    did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            inject_nasm_into_binary(mock_nasm_file, mock_target_file, None)
            pytest.fail(
                "inject_nasm_into_binary should have failed with invalid parameter but\
                    did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            inject_nasm_into_binary(mock_nasm_file, None, mock_output_file)
            pytest.fail(
                "inject_nasm_into_binary should have failed with invalid parameter but\
                    did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            inject_nasm_into_binary(None, mock_target_file, mock_output_file)
            pytest.fail(
                "inject_nasm_into_binary should have failed with invalid parameter but\
                    did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            inject_nasm_into_binary(
                mock_nasm_file,
                mock_target_file,
                mock_output_file,
                patch_entrypoint="Invalid",
            )
            pytest.fail(
                "inject_nasm_into_binary should have failed with invalid parameter but\
                    did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            inject_nasm_into_binary(
                mock_nasm_file,
                mock_target_file,
                mock_output_file,
                patch_exit="Invalid",
            )
            pytest.fail(
                "inject_nasm_into_binary should have failed with invalid parameter but\
                    did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_injector_creates_output_file(self):
        nasm_file = HELLO_WORLD_ASM
        target_file = CPP_BIN
        output_file = "/tmp/cpp_copy"

        inject_nasm_into_binary(nasm_file, target_file, output_filepath=output_file)

        assert Path(output_file).exists()

        file_size = Path(output_file).stat().st_size

        # Cleanup
        Path(output_file).unlink()

        assert file_size == Path(target_file).stat().st_size

    def test_inject_injects_shellcode_bytes_at_offset(self):
        nasm_file = HELLO_WORLD_ASM
        target_file = CRONTAB_BIN
        output_file = "/tmp/cron_copy"

        inject_nasm_into_binary(nasm_file, target_file, output_filepath=output_file)
        shellcode = bytearray(_get_shellcode_from_nasm(nasm_file)[0])

        assert len(shellcode) != 0
        assert Path(output_file).exists()

        with open(output_file, "rb") as file:
            byte_array = bytearray(file.read())

        # Cleanup
        Path(output_file).unlink()

        # Ensure that the sequence of shellcode bytes is somewhere in the file.
        assert any(
            [
                shellcode == byte_array[i : i + len(shellcode)]
                for i in range(1 + (len(byte_array) - len(shellcode)))
            ]
        )

    def test_inject_can_change_entrypoint(self):
        nasm_file = HELLO_WORLD_ASM
        target_file = CRONTAB_BIN
        output_file = "/tmp/cron_copy"

        inject_nasm_into_binary(
            nasm_file,
            target_file,
            patch_entrypoint=True,
            output_filepath=output_file,
        )

        assert Path(output_file).exists()

        with open(output_file, "rb") as patched_file:
            # 0x18 is the entrypoint offset
            patched_file.seek(0x18)
            # The entrypoint is a 8-byte value, but we only write 32-bits.
            patched_entrypoint = patched_file.read(4)

        # Cleanup
        Path(output_file).unlink()

        # Hard-coded code cave offset value
        crontab_code_cave = 0x62F1
        assert patched_entrypoint == bytearray(
            to_little_endian_32bit(crontab_code_cave)
        )


class TestGetShellcodeFromASM:
    def test_invalid_parameters(self):
        try:
            _get_shellcode_from_nasm(None)
            pytest.fail(
                "get_shellcode_from_asm should have failed with invalid parameter but\
                    did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _get_shellcode_from_nasm(True)
            pytest.fail(
                "get_shellcode_from_asm should have failed with invalid parameter but\
                    did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _get_shellcode_from_nasm("/invalid/path")
            pytest.fail(
                "get_shellcode_from_asm should have failed with file not found but\
                    did not."
            )
        except FileNotFoundError:
            pass

    def test_gets_shellcode_from_asm_hello_world(self):
        bytes_content, bytes_filename = _get_shellcode_from_nasm(HELLO_WORLD_ASM)
        assert len(bytes_content) > 0
        assert bytes_content == [
            int("b8", 16),
            int("01", 16),
            int("00", 16),
            int("00", 16),
            int("00", 16),
            int("bf", 16),
            int("01", 16),
            int("00", 16),
            int("00", 16),
            int("00", 16),
            int("48", 16),
            int("8d", 16),
            int("35", 16),
            int("10", 16),
            int("00", 16),
            int("00", 16),
            int("00", 16),
            int("ba", 16),
            int("07", 16),
            int("00", 16),
            int("00", 16),
            int("00", 16),
            int("0f", 16),
            int("05", 16),
            int("31", 16),
            int("ff", 16),
            int("b8", 16),
            int("3c", 16),
            int("00", 16),
            int("00", 16),
            int("00", 16),
            int("0f", 16),
            int("05", 16),
            int("69", 16),
            int("6e", 16),
            int("6a", 16),
            int("65", 16),
            int("63", 16),
            int("74", 16),
            int("00", 16),
        ]

        # Cleanup
        Path(bytes_filename).unlink()


class TestInjectShellcodeAtOffset:
    def test_invalid_parameters(self):
        mock_shellcode: List[int] = [0, 1, 2]
        mock_binary: str = CRONTAB_BIN
        mock_offset: int = 0x4000

        try:
            _inject_shellcode_at_offset(None, None, None)
            pytest.fail(
                "_inject_shellcode_at_offset should have failed with invalid parameter\
                    but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _inject_shellcode_at_offset(mock_shellcode, mock_binary, None)
            pytest.fail(
                "_inject_shellcode_at_offset should have failed with invalid parameter\
                    but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _inject_shellcode_at_offset(mock_shellcode, None, mock_offset)
            pytest.fail(
                "_inject_shellcode_at_offset should have failed with invalid parameter\
                    but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _inject_shellcode_at_offset(None, mock_binary, mock_offset)
            pytest.fail(
                "_inject_shellcode_at_offset should have failed with invalid parameter\
                    but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_can_inject_into_binary(self):
        mock_binary = CRONTAB_BIN

        patched_binary = _inject_shellcode_at_offset([1, 2, 3], mock_binary, 0x4000)

        # Check that the patched binary exists.
        assert Path(patched_binary).exists()

        # This test is only concerned with the binary files being different.
        cmd: str = f"diff {patched_binary} {mock_binary}"
        proc = subprocess.Popen(cmd, shell=True)
        proc.wait()

        # Cleanup
        Path(patched_binary).unlink()

        assert proc.returncode != 0

    def test_injects_into_correct_offset(self):
        mock_binary = CPP_BIN
        shellcode_bytes = [0x00, 0x50, 0xAB, 0xC4, 0x3E]
        offset = 0x21A0

        patched_binary = _inject_shellcode_at_offset(
            shellcode_bytes, mock_binary, offset
        )

        # Check that the patched binary exists.
        assert Path(patched_binary).exists()

        # Check that the file size has not changed
        assert Path(patched_binary).stat().st_size == Path(mock_binary).stat().st_size

        # Check that the bytes at the offset have been replaced.
        with open(patched_binary, "rb") as file:
            file.seek(offset)

            # Read the number of changed bytes into a bytearray
            offset_bytes = bytearray(file.read(len(shellcode_bytes)))

        # Cleanup
        Path(patched_binary).unlink()

        assert offset_bytes == bytearray(shellcode_bytes)


class TestChangeEntrypoint:
    def test_invalid_parameters(self):
        mock_target = CRONTAB_BIN
        mock_entrypoint = 0x62F1
        mock_output = "/tmp/test_output"

        try:
            _inject_shellcode_at_offset(None, None, None)
            pytest.fail(
                "change_entrypoint should have failed with invalid parameter\
                    but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _inject_shellcode_at_offset(mock_target, mock_entrypoint, None)
            pytest.fail(
                "change_entrypoint should have failed with invalid parameter\
                    but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _inject_shellcode_at_offset(mock_target, None, mock_output)
            pytest.fail(
                "change_entrypoint should have failed with invalid parameter\
                    but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _inject_shellcode_at_offset(None, mock_entrypoint, mock_output)
            pytest.fail(
                "change_entrypoint should have failed with invalid parameter\
                    but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_changes_file(self):
        mock_target = CRONTAB_BIN
        mock_entrypoint = 0x62F1

        output_file = change_entrypoint(mock_target, mock_entrypoint)

        assert Path(output_file).exists()

        # This test is only concerned with the binary files being different.
        cmd: str = f"diff {output_file} {mock_target}"
        proc = subprocess.Popen(cmd, shell=True)
        proc.wait()

        # Cleanup
        Path(output_file).unlink()

        assert proc.returncode != 0

    def test_changes_entrypoint(self):
        mock_target = CRONTAB_BIN
        mock_entrypoint = 0x62F1

        output_file = change_entrypoint(mock_target, mock_entrypoint)

        assert Path(output_file).exists()

        with open(output_file, "rb") as patched_file:
            # 0x18 is the entrypoint offset
            patched_file.seek(0x18)
            # The entrypoint is a 8-byte value, but we only write 32-bits.
            patched_entrypoint = patched_file.read(4)

        # Cleanup
        Path(output_file).unlink()

        assert patched_entrypoint == bytearray(to_little_endian_32bit(mock_entrypoint))


class TestPatchPltsecExit:
    def test_invalid_parameters(self):
        mock_target = CRONTAB_BIN
        mock_patch_offset = 0x62F1
        mock_output = "/tmp/test_output"

        try:
            _inject_shellcode_at_offset(None, None, None)
            pytest.fail(
                "patch_pltsec_exit should have failed with invalid parameter\
                    but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _inject_shellcode_at_offset(mock_target, mock_patch_offset, None)
            pytest.fail(
                "patch_pltsec_exit should have failed with invalid parameter\
                    but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _inject_shellcode_at_offset(mock_target, None, mock_output)
            pytest.fail(
                "patch_pltsec_exit should have failed with invalid parameter\
                    but did not."
            )
        except MKPKInvalidParameter:
            pass

        try:
            _inject_shellcode_at_offset(None, mock_patch_offset, mock_output)
            pytest.fail(
                "patch_pltsec_exit should have failed with invalid parameter\
                    but did not."
            )
        except MKPKInvalidParameter:
            pass

    def test_change_file(self):
        mock_target = CAT_BIN
        mock_patch_offset = 0x5C36

        output_file = patch_pltsec_exit(mock_target, mock_patch_offset)

        # Check that the output file exists
        assert Path(output_file).exists()

        # This test is only concerned with the binary files being different.
        cmd: str = f"diff {output_file} {mock_target}"
        proc = subprocess.Popen(cmd, shell=True)
        proc.wait()

        # Cleanup
        Path(output_file).unlink()

        assert proc.returncode != 0

    def test_changes_plt_sec_address(self):
        mock_target = CAT_BIN
        mock_patch_offset = 0x5C36

        output_file = patch_pltsec_exit(mock_target, mock_patch_offset)

        cmd: str = f"objdump -d {output_file} | egrep '<_?exit@plt>:'"
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        proc.wait()
        entries = proc.communicate()[0].decode("utf-8")

        # The /usr/bin/cat binary has a exit@plt and _exit@plt, however objdump will
        # remove the comments for these symbols when the address has been patched.
        assert len(entries) == 0

        cmd: str = f"chmod +x {output_file}"
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        proc.wait()

        # /usr/bin/cat calls sys_exit when the --help flag is specified, meaning
        # execution will jump to the patch offset on process exit.
        cmd: str = f"{output_file} --help"
        proc = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
        proc.wait()

        # Cleanup
        Path(output_file).unlink()

        # As the binary has not had shellcode injected into the redirect address,
        # running this binary should cause a segmentation fault.
        assert proc.returncode != 0
