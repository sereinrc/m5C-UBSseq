import os
import pandas as pd
from glob import glob

base_dir = "workspace/benchmarks"
all_files = glob(f"{base_dir}/**/*.txt", recursive=True)

# 调试：打印找到的文件
print(f"Total files found: {len(all_files)}")
if not all_files:
    print("Error: No files found. Check base_dir path.")
    exit()

data_list = []

for file_path in all_files:
    print(f"\nProcessing: {file_path}")
    
    dir_path, filename = os.path.split(file_path)
    rule_name = os.path.basename(dir_path)
    
    # 解析文件名
    if "_contamination" in filename:
        sample = filename.split("_contamination")[0]
        ref_type = "contamination"
    elif "_genes" in filename:
        sample = filename.split("_genes")[0]
        ref_type = "genes"
    elif "_genome" in filename:
        sample = filename.split("_genome")[0]
        ref_type = "genome"
    else:
        sample = filename.split(".")[0]
        ref_type = "general"
    
    # 处理包含运行编号的样本名（如 WT-rep1_run1 -> WT-rep1）
    if "_run" in sample:
        sample = sample.split("_run")[0]

    try:
        df = pd.read_csv(file_path, sep="\t")
        if df.empty:
            print(f"Skipping empty file: {filename}")
            continue
        
        df["rule_name"] = rule_name
        df["sample"] = sample
        df["reference_type"] = ref_type
        data_list.append(df)
        print(f"Added {len(df)} rows from {filename}")

    except Exception as e:
        print(f"Failed to process {filename}: {str(e)}")

if not data_list:
    print("No data to concatenate. Exiting.")
    exit()

# 合并数据
combined_df = pd.concat(data_list, ignore_index=True)

# 选择需要的列
columns_to_keep = [
    'sample', 'rule_name', 'reference_type',
    's', 'h:m:s', 'max_rss', 'max_vms', 'max_uss', 'max_pss',
    'io_in', 'io_out', 'mean_load', 'cpu_time', 'threads',
    'cpu_usage', 'input_size_mb'
]

final_df = combined_df[columns_to_keep]

# 保存结果
output_file = "workspace/benchmark_stats.csv"
final_df.to_csv(output_file, index=False)
print(f"\nSuccess: Saved results to {output_file}")