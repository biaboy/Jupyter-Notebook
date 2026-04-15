# ===================== 日志配置（必加，定时任务必须有）=====================
import logging
import os
from datetime import datetime

# 自动生成日志文件（和脚本同一目录）
script_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(script_dir, "auto_export.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=log_file,
    filemode="a",
    encoding="utf-8"
)


try:
    logging.info("===== 开始执行 2026抖音电商数据导出任务 =====")

    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib import rcParams

    ## 字体设置（解决中文乱码）
    rcParams['font.sans-serif'] = 'SimHei'
    rcParams['axes.unicode_minus'] = False
    import seaborn as sns

    df = pd.read_csv('C:/Users\Administrator\Desktop/douyin.csv')
    #缺失值处理
    df.drop(columns='brand_clean', inplace=True)
    df.drop(columns='shop_id', inplace=True)
    df.dropna(subset=['c1_id'], inplace=True)
    df[['user_id', 'shop_name']] = df[['user_id', 'shop_name']].fillna(0)
    #重复值处理
    df = df.drop_duplicates()
#列重命名为中文
    columns = ['商单号','商品名称','用户ID','品牌',
           '店铺','一级类目ID','一级类目','二级类目ID',
           '二级类目','三级类目ID','三级类目','GMV',
           '售出数量'
    ]
    df.columns = columns
    gmv_result = df.groupby("一级类目")["GMV"].sum().reset_index()
    gmv_result = gmv_result.sort_values(by="GMV", ascending=False)

# 打印统计结果
    print("===== 按一级类目GMV统计结果 =====")
    print(gmv_result)

#可视化：GMV对比柱状图
    plt.figure(figsize=(10, 6))  # 设置画布大小
    bars = plt.bar(gmv_result["一级类目"], gmv_result["GMV"], color="#1f77b4", width=0.6)

# 给柱子添加数值标签
    for bar in bars:
        height = bar.get_height()
    # 数值格式化：大额取整，小额保留1位小数
        label_text = f"{int(height)}" if height > 1000 else f"{height:.1f}"
        plt.text(bar.get_x() + bar.get_width()/2, height + 500,
             label_text, ha="center", va="bottom", fontsize=10)

# 图表美化
    plt.title("各一级类目GMV总额对比", fontsize=14, fontweight="bold")
    plt.xlabel("一级类目", fontsize=12)
    plt.ylabel("GMV（元）", fontsize=12)
    plt.xticks(rotation=30)
    plt.grid(axis="y", linestyle="--", alpha=0.7)  # 添加横向网格线
    plt.tight_layout()
    plt.show()

# 可视化：GMV占比饼图
    plt.figure(figsize=(8, 8))
    plt.pie(gmv_result["GMV"],
        labels=gmv_result["一级类目"],
        autopct="%1.2f%%",  # 显示百分比
        startangle=90,
        textprops={"fontsize": 10})
    plt.title("各一级类目GMV占比", fontsize=14, fontweight="bold")
    plt.axis("equal")
    plt.tight_layout()
    plt.show()
#------------------分析上方一级类目最大占比的二级类目----------------------------------
##===============个护化妆 ================
    df_filter = df[(df['一级类目'] == '个护化妆')]

# 按二级类目分组统计GMV总和，降序排序
    gmv_result = df_filter.groupby("二级类目")["GMV"].sum().reset_index()
    gmv_result = gmv_result.sort_values(by="GMV", ascending=False)

# 打印统计结果，核对数据
    print("===== 二级类目GMV统计结果 =====")
    print(gmv_result)

#可视化：GMV对比柱状图
    plt.figure(figsize=(8, 5))
    bars = plt.bar(gmv_result["二级类目"], gmv_result["GMV"], color="#ff7f0e", width=0.5)

# 给柱子添加数值标签
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 1000,
             f"{int(height)}", ha="center", va="bottom", fontsize=11)

# 图表美化
    plt.title("个护化妆-二级类目GMV对比", fontsize=14, fontweight="bold")
    plt.xlabel("二级类目", fontsize=12)
    plt.ylabel("GMV（元）", fontsize=12)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()

# 可视化：GMV占比饼图
    plt.figure(figsize=(7, 7))
    plt.pie(gmv_result["GMV"],
        labels=gmv_result["二级类目"],
        autopct="%1.2f%%",
        startangle=90,
        textprops={"fontsize": 11},
        colors=["#ff7f0e", "#1f77b4"])
    plt.title("个护化妆-二级类目GMV占比", fontsize=14, fontweight="bold")
    plt.axis("equal")
    plt.tight_layout()
    plt.show()

##===============服装=================
    df_filter = df[(df['一级类目'] == '服装')]

# 按二级类目分组统计GMV总和，降序排序
    gmv_result = df_filter.groupby("二级类目")["GMV"].sum().reset_index()
    gmv_result = gmv_result.sort_values(by="GMV", ascending=False)

# 打印统计结果，核对数据
    print("===== 二级类目GMV统计结果 =====")
    print(gmv_result)

# 可视化：GMV对比柱状图
    plt.figure(figsize=(8, 5))
    bars = plt.bar(gmv_result["二级类目"], gmv_result["GMV"], color="#ff7f0e", width=0.5)

# 给柱子添加数值标签
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 1000,
             f"{int(height)}", ha="center", va="bottom", fontsize=11)

# 图表美化
    plt.title("服装-二级类目GMV对比", fontsize=14, fontweight="bold")
    plt.xlabel("二级类目", fontsize=12)
    plt.ylabel("GMV（元）", fontsize=12)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()

# 可视化：GMV占比饼图
    plt.figure(figsize=(7, 7))
    plt.pie(gmv_result["GMV"],
        labels=gmv_result["二级类目"],
        autopct="%1.2f%%",
        startangle=90,
        textprops={"fontsize": 11},
        colors=["#ff7f0e", "#1f77b4"])
    plt.title("服装-二级类目GMV占比", fontsize=14, fontweight="bold")
    plt.axis("equal")
    plt.tight_layout()
    plt.show()


#------------------分析上方二级类目最大占比的三级类目----------------------------------
##===============面部护肤 ================
    df_filter = df[(df['二级类目'] == '面部护肤')]

# 按三级类目分组统计GMV总和，降序排序
    gmv_result = df_filter.groupby("三级类目")["GMV"].sum().reset_index()
    gmv_result = gmv_result.sort_values(by="GMV", ascending=False)

# 打印统计结果，核对数据
    print("===== 三级类目GMV统计结果 =====")
    print(gmv_result)

# 可视化：GMV对比柱状图
    plt.figure(figsize=(8, 5))
    bars = plt.bar(gmv_result["三级类目"], gmv_result["GMV"], color="#ff7f0e", width=0.5)

# 给柱子添加数值标签
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 1000,
             f"{int(height)}", ha="center", va="bottom", fontsize=11)

# 图表美化
    plt.title("个护化妆-三级类目GMV对比", fontsize=14, fontweight="bold")
    plt.xlabel("三级类目", fontsize=12)
    plt.ylabel("GMV（元）", fontsize=12)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()

# 可视化：GMV占比饼图
    plt.figure(figsize=(7, 7))
    plt.pie(gmv_result["GMV"],
        labels=gmv_result["三级类目"],
        autopct="%1.2f%%",
        startangle=90,
        textprops={"fontsize": 11},
        colors=["#ff7f0e", "#1f77b4"])
    plt.title("个护化妆-三级类目GMV占比", fontsize=14, fontweight="bold")
    plt.axis("equal")
    plt.tight_layout()
    plt.show()

#=====================女装=====================
    df_filter = df[(df['二级类目'] == '女装')]

# 按三级类目分组统计GMV总和，降序排序
    gmv_result = df_filter.groupby("三级类目")["GMV"].sum().reset_index()
    gmv_result = gmv_result.sort_values(by="GMV", ascending=False)

# 打印统计结果，核对数据
    print("===== 三级类目GMV统计结果 =====")
    print(gmv_result)

# 可视化：GMV对比柱状图
    plt.figure(figsize=(8, 5))
    bars = plt.bar(gmv_result["三级类目"], gmv_result["GMV"], color="#ff7f0e", width=0.5)

# 给柱子添加数值标签
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 1000,
             f"{int(height)}", ha="center", va="bottom", fontsize=11)

# 图表美化
    plt.title("个护化妆-三级类目GMV对比", fontsize=14, fontweight="bold")
    plt.xlabel("三级类目", fontsize=12)
    plt.ylabel("GMV（元）", fontsize=12)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()

# 可视化：GMV占比饼图
    plt.figure(figsize=(7, 7))
    plt.pie(gmv_result["GMV"],
        labels=gmv_result["三级类目"],
        autopct="%1.2f%%",
        startangle=90,
        textprops={"fontsize": 11},
        colors=["#ff7f0e", "#1f77b4"])
    plt.title("个护化妆-三级类目GMV占比", fontsize=14, fontweight="bold")
    plt.axis("equal")
    plt.tight_layout()
    plt.show()

#------------------分析上方三级类目最大占比的品牌----------------------------------
##==================品牌=======================
    df_filter = df[(df['三级类目'] == '护肤套装')]

    # 按品牌分组统计GMV总和，降序排序
    gmv_result = df_filter.groupby("品牌")["GMV"].sum().reset_index()
    gmv_result = gmv_result.sort_values(by="GMV", ascending=False)

    print("===== 品牌GMV统计结果 =====")
    print(gmv_result)

    plt.figure(figsize=(7, 7))
    plt.pie(gmv_result["GMV"],
        labels=gmv_result["品牌"],
        autopct="%1.2f%%",
        startangle=90,
        textprops={"fontsize": 11},
        colors=["#ff7f0e", "#1f77b4"])
    plt.title("护肤套装-品牌GMV占比", fontsize=14, fontweight="bold")
    plt.axis("equal")
    plt.tight_layout()
    plt.show()

##==================女士连衣裙=======================
    df_filter = df[(df['三级类目'] == '女士连衣裙')]

# 按品牌分组统计GMV总和，降序排序
    gmv_result = df_filter.groupby("品牌")["GMV"].sum().reset_index()
    gmv_result = gmv_result.sort_values(by="GMV", ascending=False)

# 打印统计结果，核对数据
    print("===== 品牌GMV统计结果 =====")
    print(gmv_result)

# 可视化：GMV占比饼图（看类目贡献度）
    plt.figure(figsize=(7, 7))
    plt.pie(gmv_result["GMV"],
        labels=gmv_result["品牌"],
        autopct="%1.2f%%",
        startangle=90,
        textprops={"fontsize": 11},
        colors=["#ff7f0e", "#1f77b4"])
    plt.title("连衣裙-品牌GMV占比", fontsize=14, fontweight="bold")
    plt.axis("equal")  # 保证饼图是正圆形
    plt.tight_layout()
    plt.show()


# 导出Excel

    df_clean = df
    file_path = r"C:\Users\Administrator\Desktop\抖音电商清洗数据.csv"

    
    df_clean.to_csv(
        file_path,
        index=False,
        encoding="utf-8-sig"
    )


    logging.info(f"✅ 文件导出成功！路径：{file_path}")
    logging.info("===== 任务全部执行完成 =====")

except Exception as e:
    logging.error("❌ 任务执行失败，错误信息如下：", exc_info=True)
