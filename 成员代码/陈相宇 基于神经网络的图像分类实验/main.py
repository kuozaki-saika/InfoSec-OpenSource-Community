"""
main.py - 基于神经网络的图像分类实验（含安全模块）
===================================================
集成功能：
 1. CNN 图像分类实验（MNIST / CIFAR-10）
 2. 密码管理系统（注册、登录、密码重置、安全控制点验证）
 3. 安全扫描工具（代码审计、依赖检查、报告生成）
 4. 文档汇总（risk-analysis、constraint-doc、checklist）

作者：陈相宇
日期：2026-06-30
"""

import sys
import os

# 确保 Windows 控制台支持 UTF-8 输出
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# 将当前目录加入搜索路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cnn_classifier import (
    check_environment, load_and_preprocess_data,
    create_cnn_model, compile_model, train_model,
    plot_training_history, evaluate_model, main as cnn_main
)
from security.password_manager import PasswordManager
from security.security_scanner import SecurityScanner


def show_banner():
    """显示项目横幅"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║     基于神经网络的图像分类实验（含安全模块）                     ║
║     Neural Network Image Classification with Security Module     ║
║                                                                  ║
║     作者：陈相宇                                                 ║
║     日期：2026-06-30                                             ║
╚══════════════════════════════════════════════════════════════════╝
    """)


def menu_image_classification():
    """子菜单：图像分类实验"""
    print("\n" + "=" * 60)
    print("  [1] 图像分类实验")
    print("=" * 60)
    print("  1. MNIST 手写数字分类（快速）")
    print("  2. CIFAR-10 彩色图像分类")
    print("  3. 返回主菜单")
    print("-" * 60)
    choice = input("请选择 (1-3): ").strip()

    if choice in ('1', '2'):
        dataset = 'mnist' if choice == '1' else 'cifar10'
        print(f"\n启动 {dataset.upper()} 图像分类实验...")
        print("提示：这将开始模型训练，可能需要几分钟时间。")
        confirm = input("确认运行？(y/n): ").strip().lower()
        if confirm == 'y':
            cnn_main()
    return choice != '3'


def menu_password_management():
    """子菜单：密码管理系统"""
    print("\n" + "=" * 60)
    print("  [2] 密码管理系统")
    print("=" * 60)
    PasswordManager.run_interactive_demo()


def menu_security_scan():
    """子菜单：安全扫描工具"""
    print("\n" + "=" * 60)
    print("  [3] 安全扫描工具")
    print("=" * 60)
    print("  运行完整安全扫描，生成 reports/ 报告文件...")
    print()

    scanner = SecurityScanner(
        project_root=os.path.dirname(os.path.abspath(__file__)),
        output_dir="reports",
    )
    results = scanner.run_full_scan()

    score = results['security_score']
    print(f"\n扫描结果摘要：")
    print(f"  安全评分：{score['total_score']}/100 ({score['grade']})")
    print(f"  危险函数调用：{len(results['dangerous_functions'])} 个")
    print(f"  硬编码密钥：{len(results['hardcoded_secrets'])} 个")
    print(f"  依赖漏洞：{len(results['dependencies']['vulnerable'])} 个")

    input("\n按 Enter 返回主菜单...")


def menu_docs():
    """子菜单：查看文档"""
    print("\n" + "=" * 60)
    print("  [4] 安全文档")
    print("=" * 60)
    print("  1. 风险分析报告 (docs/risk-analysis.md)")
    print("  2. 约束文档 (docs/constraint-doc.md)")
    print("  3. 安全检查清单 (docs/checklist.md)")
    print("  4. 查看安全扫描报告 (reports/)")
    print("  5. 返回主菜单")
    print("-" * 60)
    choice = input("请选择 (1-5): ").strip()

    docs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
    reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")

    doc_files = {
        '1': os.path.join(docs_dir, 'risk-analysis.md'),
        '2': os.path.join(docs_dir, 'constraint-doc.md'),
        '3': os.path.join(docs_dir, 'checklist.md'),
    }

    if choice in doc_files:
        filepath = doc_files[choice]
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            print("\n" + "=" * 60)
            print(f"  {os.path.basename(filepath)}")
            print("=" * 60)
            print(content[:2000])  # 显示前2000字符
            if len(content) > 2000:
                print(f"\n... (共 {len(content)} 字符，已截断显示)")
        else:
            print(f"文件不存在: {filepath}")
    elif choice == '4':
        if os.path.exists(reports_dir):
            report_files = sorted(os.listdir(reports_dir), reverse=True)
            print(f"\nreports/ 目录下的文件 ({len(report_files)} 个)：")
            for rf in report_files[:10]:
                print(f"  - {rf}")
        else:
            print("reports/ 目录不存在，请先运行安全扫描")
    elif choice == '5':
        pass

    if choice != '5':
        input("\n按 Enter 返回主菜单...")
    return True


def main():
    """主菜单"""
    while True:
        show_banner()
        print("请选择功能模块：")
        print("  1. 图像分类实验 (MNIST / CIFAR-10)")
        print("  2. 密码管理系统 (注册 / 登录 / 密码重置)")
        print("  3. 安全扫描工具 (代码审计 + 报告生成)")
        print("  4. 安全文档 (风险分析 / 约束 / 检查清单)")
        print("  5. 退出")
        print("-" * 60)
        choice = input("请选择 (1-5): ").strip()

        if choice == '1':
            if not menu_image_classification():
                continue
        elif choice == '2':
            menu_password_management()
        elif choice == '3':
            menu_security_scan()
        elif choice == '4':
            menu_docs()
        elif choice == '5':
            print("\n感谢使用！再见！")
            break
        else:
            print("无效选项，请重新选择")


if __name__ == "__main__":
    main()
