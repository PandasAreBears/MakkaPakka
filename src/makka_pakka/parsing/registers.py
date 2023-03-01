__pointer_registers_letters = ["sp", "bp", "ip"]
__pointer_register_variant_transformations = [
    lambda ltrs: f"r{ltrs}",
    lambda ltrs: f"e{ltrs}",
    lambda ltrs: f"{ltrs}",
]
__pointer_registers = [
    func(ltrs)
    for ltrs in __pointer_registers_letters
    for func in __pointer_register_variant_transformations
]

__data_register_variant_transforms = [
    lambda ltr: f"r{ltr}x",
    lambda ltr: f"e{ltr}x",
    lambda ltr: f"{ltr}x",
    lambda ltr: f"{ltr}h",
    lambda ltr: f"{ltr}ltr",
]
__data_register_letters = ["a", "b", "c", "d"]
__data_registers = [
    func(ltr)
    for ltr in __data_register_letters
    for func in __data_register_variant_transforms
]

__index_register_letters = ["si", "di"]
__index_register_variant_transformations = [
    lambda ltrs: f"r{ltrs}",
    lambda ltrs: f"e{ltrs}",
    lambda ltrs: f"{ltrs}",
]
__index_registers = [
    func(ltrs)
    for ltrs in __index_register_letters
    for func in __index_register_variant_transformations
]

__other_registers = ["r8", "r9", "r10"]

REGISTER_NAMES = (
    __pointer_registers + __data_registers + __index_registers + __other_registers
)
