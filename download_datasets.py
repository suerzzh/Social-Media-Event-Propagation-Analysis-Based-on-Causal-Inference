"""
数据集下载脚本
用于下载推荐的公开数据集
"""

import os
import requests
import zipfile
from pathlib import Path

# 创建数据目录
DATA_DIR = Path("data/public_datasets")
DATA_DIR.mkdir(parents=True, exist_ok=True)

def download_file(url, filename, description):
    """下载文件"""
    filepath = DATA_DIR / filename
    
    if filepath.exists():
        print(f"✅ {description} 已存在: {filepath}")
        return filepath
    
    print(f"📥 正在下载 {description}...")
    print(f"   链接: {url}")
    
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"   进度: {percent:.1f}%", end='\r')
        
        print(f"\n✅ {description} 下载完成: {filepath}")
        return filepath
    
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        return None

def extract_zip(filepath, extract_to=None):
    """解压ZIP文件"""
    if not filepath or not filepath.exists():
        return
    
    if extract_to is None:
        extract_to = filepath.parent / filepath.stem
    
    print(f"📦 正在解压 {filepath.name}...")
    try:
        with zipfile.ZipFile(filepath, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print(f"✅ 解压完成: {extract_to}")
    except Exception as e:
        print(f"❌ 解压失败: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("公开数据集下载工具")
    print("=" * 60)
    
    datasets = [
        {
            "name": "Twitter 15 Dataset",
            "url": "https://www.cs.ucsb.edu/~william/data/Twitter15.zip",
            "filename": "Twitter15.zip",
            "description": "Twitter 15 数据集（2015年Twitter新闻传播数据）"
        },
        {
            "name": "Twitter 16 Dataset",
            "url": "https://www.cs.ucsb.edu/~william/data/Twitter16.zip",
            "filename": "Twitter16.zip",
            "description": "Twitter 16 数据集（2016年Twitter新闻传播数据）"
        }
    ]
    
    print("\n可下载的数据集:")
    for i, dataset in enumerate(datasets, 1):
        print(f"{i}. {dataset['name']}")
    
    print("\n注意:")
    print("- 其他数据集需要从GitHub或论文页面下载")
    print("- 部分数据集需要注册或API密钥")
    print("- 建议手动下载Weibo数据集（GitHub）")
    
    # 下载数据集
    for dataset in datasets:
        print(f"\n{'='*60}")
        filepath = download_file(
            dataset['url'],
            dataset['filename'],
            dataset['description']
        )
        
        # 如果是ZIP文件，询问是否解压
        if filepath and filepath.suffix == '.zip':
            response = input(f"\n是否解压 {dataset['filename']}? (y/n): ")
            if response.lower() == 'y':
                extract_zip(filepath)
    
    print("\n" + "=" * 60)
    print("下载完成！")
    print(f"数据保存在: {DATA_DIR.absolute()}")
    print("\n其他数据集下载方式:")
    print("1. Weibo数据集: https://github.com/ICTMCG/Characterizing-Weibo-Multi-Domain-False-News")
    print("2. PHEME数据集: https://figshare.com/articles/dataset/PHEME_dataset_for_Rumour_Detection_and_Veracity_Classification/6392078")
    print("3. TimeGraph/CausalTime: 访问论文GitHub仓库")
    print("4. Tigramite示例: pip install tigramite")

if __name__ == "__main__":
    main()

