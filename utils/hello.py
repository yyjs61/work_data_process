def db_to_again(db_value, cg_ratio=8.3):
    """
    将 HCG 的 dB 值转换为 again（线性模拟增益）
    公式: 10 ** ((db + cg_ratio) / 20)
    """
    return 10 ** ((db_value + cg_ratio) / 20)

# === 使用示例 ===
if __name__ == "__main__":
    # 1. 单个值计算
    db = 33.0
    again = db_to_again(db)
    print(f"dB = {db}  =>  again ≈ {again:.6f}\n")
    print(f"again ≈ {again:.6f} => iso ≈ {again * 50:.6f} \n")

    # # 2. 批量计算（列表推导式）
    # db_list = [-10.0, 0.0, 6.0, 20.0]
    # again_list = [db_to_again(d) for d in db_list]
    # for d, a in zip(db_list, again_list):
    #     print(f"dB = {d:5.1f}  =>  again ≈ {a:.6f}")