import logging
import os
from datetime import datetime, timedelta



#定时任务日志文件
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
    import seaborn as sns

    ## 字体设置（解决中文乱码）
    rcParams['font.sans-serif'] = 'SimHei'
    rcParams['axes.unicode_minus'] = False


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
    #=================================GMV计算==================================
    # 统计用户数
    print(f"用户数量: {df['用户ID'].nunique()}")

    # 移除用户ID为0的记录
    df = df[df['用户ID'] != 0]
    print(f"\n移除用户ID为0后的数据量: {len(df)}")

    # 添加模拟的购买日期列
    np.random.seed(42)
    current_date = datetime.now()
    df['购买日期'] = [current_date - timedelta(days=np.random.randint(1, 90)) for _ in range(len(df))]

    # 计算RFM指标
    rfm_df = df.groupby('用户ID').agg({
        'GMV': ['sum', 'count'],
        '购买日期': 'max'
    })

    # 重命名列
    rfm_df.columns = ['Monetary', 'Frequency', '最近购买日期']

    # 计算Recency
    rfm_df['Recency'] = (current_date - rfm_df['最近购买日期']).dt.days
    rfm_df = rfm_df.drop('最近购买日期', axis=1)

    # 对RFM指标进行标准化
    from sklearn.preprocessing import StandardScaler

    scaler = StandardScaler()
    rfm_scaled = scaler.fit_transform(rfm_df)
    rfm_scaled = pd.DataFrame(rfm_scaled, index=rfm_df.index, columns=rfm_df.columns)

    # 使用K-means聚类进行客户分群
    from sklearn.cluster import KMeans

    # 确定最佳聚类数
    inertia = []
    for k in range(1, 11):
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(rfm_scaled)
        inertia.append(kmeans.inertia_)

    # 绘制肘部图
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, 11), inertia, marker='o')
    plt.title('肘部法则确定最佳聚类数')
    plt.xlabel('聚类数')
    plt.ylabel('惯性')
    plt.savefig('c:\\Users\\Administrator\\Desktop\\肘部图.png')
    plt.show()

    # 根据上图得到最佳聚类数4
    n_clusters = 4
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    rfm_df['Cluster'] = kmeans.fit_predict(rfm_scaled)

    # 分析每个聚类的特征
    print("\n各聚类的RFM特征：")
    cluster_analysis = rfm_df.groupby('Cluster').agg({
        'Recency': 'mean',
        'Frequency': 'mean',
        'Monetary': 'mean',
        'Cluster': 'count'
    }).rename(columns={'Cluster': 'Customer Count'})
    print(cluster_analysis)


    # 客户分群命名
    def get_customer_segment(row):
        cluster = row['Cluster']
        if cluster == 0:
            return '低价值客户'
        elif cluster == 1:
            return '高价值客户'
        elif cluster == 2:
            return '中等价值客户'
        else:
            return '潜在价值客户'


    rfm_df['Segment'] = rfm_df.apply(get_customer_segment, axis=1)

    # 统计各客户群体数量
    segment_counts = rfm_df['Segment'].value_counts()
    print("\n各客户群体数量：")
    print(segment_counts)

    # 可视化客户群体分布
    plt.figure(figsize=(10, 6))
    segment_counts.plot(kind='bar', color='skyblue')
    plt.title('客户群体分布')
    plt.xlabel('客户群体')
    plt.ylabel('数量')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('c:\\Users\\Administrator\\Desktop\\客户群体分布.png')
    plt.show()

    # 保存RFM分析结果
    rfm_df.to_csv('c:\\Users\\Administrator\\Desktop\\RFM分析结果.csv')
    print("\nRFM分析结果已保存到：c:\\Users\\Administrator\\Desktop\\RFM分析结果.csv")

    # 打印分析总结
    print("\nRFM分析总结：")
    print(f"总用户数: {len(rfm_df)}")
    print(f"平均购买频率: {rfm_df['Frequency'].mean():.2f}")
    print(f"平均消费金额: {rfm_df['Monetary'].mean():.2f}")
    print(f"平均Recency: {rfm_df['Recency'].mean():.2f}天")
    print(f"客户群体数量: {rfm_df['Segment'].nunique()}")


    #=======================================GMV分析===================================

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
