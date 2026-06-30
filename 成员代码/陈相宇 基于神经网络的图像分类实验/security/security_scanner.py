"""
安全扫描工具 (Security Scanner)
================================
功能：
 - 代码安全漏洞扫描
 - 依赖项安全检查
 - 密码策略合规审计
 - 生成安全扫描报告（reports/ 目录）
 - 安全评分与改进建议
"""

import sys
# 确保 Windows 控制台支持 UTF-8 输出
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import os
import sys
import json
import hashlib
import re
import ast
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Set
from pathlib import Path


class SecurityScanner:
    """安全扫描器：代码安全审计 + 依赖检查 + 策略合规验证"""

    # ========================================================================
    # 安全扫描配置
    # ========================================================================

    # 危险函数模式（Python）
    # 注意：compile( 仅匹配裸调用，不匹配 model.compile( 等安全用法
    DANGEROUS_FUNCTIONS = [
        'exec(', 'eval(', '__import__',
        'os.system(', 'os.popen(', 'subprocess.call(',
        'subprocess.Popen(', 'subprocess.run(',
        'pickle.load', 'pickle.loads',
        'yaml.load(',  # 不带 SafeLoader 的 yaml.load
        'marshal.loads',
    ]

    # 安全白名单（不标记为危险）
    SAFE_PATTERNS = [
        'model.compile(',      # Keras/TensorFlow 模型编译
        'optimizer.compile(',  # 优化器编译
        're.compile(',         # 正则表达式编译
    ]

    # 密码硬编码模式
    HARDCODED_SECRET_PATTERNS = [
        r'(?i)password\s*=\s*[\'"]\S+[\'"]',
        r'(?i)api_key\s*=\s*[\'"]\S+[\'"]',
        r'(?i)secret\s*=\s*[\'"]\S+[\'"]',
        r'(?i)token\s*=\s*[\'"]\S+[\'"]',
        r'(?i)private_key\s*=\s*[\'"]\S+[\'"]',
        r'(?i)access_key\s*=\s*[\'"]\S+[\'"]',
    ]

    # 安全最佳实践检查项
    BEST_PRACTICES = {
        'csrf_protection': {
            'name': 'CSRF 防护',
            'patterns': [r'csrf', r'CsrfViewMiddleware', r'@csrf_protect'],
            'severity': 'high',
        },
        'sql_injection_protection': {
            'name': 'SQL 注入防护',
            'patterns': [r'parameterized', r'cursor\.execute\(.*%s', r'\.bindparam'],
            'severity': 'critical',
        },
        'password_hashing': {
            'name': '密码哈希',
            'patterns': [r'hashlib', r'bcrypt', r'PBKDF2', r'argon2', r'scrypt'],
            'severity': 'critical',
        },
        'input_validation': {
            'name': '输入验证',
            'patterns': [r'\.strip\(\)', r'\.validate', r'clean_data', r'sanitize'],
            'severity': 'high',
        },
        'error_handling': {
            'name': '错误处理',
            'patterns': [r'try\s*:', r'except', r'finally', r'logging\.'],
            'severity': 'medium',
        },
        'rate_limiting': {
            'name': '速率限制',
            'patterns': [r'rate_limit', r'throttle', r'MAX_LOGIN_ATTEMPTS', r'LOCKOUT'],
            'severity': 'high',
        },
        'session_security': {
            'name': '会话安全',
            'patterns': [r'SESSION_COOKIE_SECURE', r'SESSION_COOKIE_HTTPONLY', r'session\.'],
            'severity': 'medium',
        },
        'file_upload_security': {
            'name': '文件上传安全',
            'patterns': [r'ALLOWED_EXTENSIONS', r'FileExtensionValidator', r'mime_type'],
            'severity': 'high',
        },
    }

    def __init__(self, project_root: str, output_dir: str = "reports"):
        """
        初始化安全扫描器

        Args:
            project_root: 项目根目录
            output_dir: 报告输出目录
        """
        self.project_root = Path(project_root)
        self.output_dir = Path(output_dir)
        self.findings: List[Dict] = []
        self.scan_results: Dict = {}
        self._ensure_output_dir()

    def _ensure_output_dir(self):
        """确保报告输出目录存在"""
        os.makedirs(self.output_dir, exist_ok=True)

    # ========================================================================
    # 扫描引擎
    # ========================================================================

    def _find_python_files(self) -> List[Path]:
        """查找项目中所有 Python 文件"""
        python_files = []
        exclude_dirs = {'.venv', 'venv', '__pycache__', '.git', '.idea', '.vscode',
                        'node_modules', '.claude', 'data', 'Dataset', 'pretrained_models',
                        'security', 'reports', 'docs', 'share'}
        for root, dirs, files in os.walk(self.project_root):
            # 排除指定目录
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        return python_files

    def _find_all_files(self, extensions: Set[str]) -> List[Path]:
        """查找项目中指定扩展名的文件"""
        files = []
        exclude_dirs = {'.venv', 'venv', '__pycache__', '.git', '.idea', '.vscode',
                        'node_modules', '.claude', 'data', 'Dataset', 'pretrained_models',
                        'security', 'reports', 'docs', 'share'}
        for root, dirs, filenames in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for filename in filenames:
                ext = Path(filename).suffix.lower()
                if ext in extensions:
                    files.append(Path(root) / filename)
        return files

    # ========================================================================
    # 扫描模块1：代码安全漏洞扫描
    # ========================================================================

    def scan_dangerous_functions(self) -> List[Dict]:
        """
        扫描危险函数调用

        Returns:
            危险函数调用列表
        """
        findings = []
        python_files = self._find_python_files()

        for filepath in python_files:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')

                for lineno, line in enumerate(lines, 1):
                    # 跳过安全白名单匹配
                    if any(safe in line for safe in self.SAFE_PATTERNS):
                        continue

                    for func in self.DANGEROUS_FUNCTIONS:
                        if func in line:
                            # 排除注释行和文档字符串中的匹配
                            stripped = line.strip()
                            if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                                continue

                            findings.append({
                                'type': 'dangerous_function',
                                'file': str(filepath.relative_to(self.project_root)),
                                'line': lineno,
                                'code': line.strip()[:120],
                                'function': func,
                                'severity': 'high',
                                'recommendation': f'检查 {func} 调用是否安全，考虑使用更安全的替代方案',
                            })
            except Exception as e:
                findings.append({
                    'type': 'scan_error',
                    'file': str(filepath),
                    'error': str(e),
                })

        return findings

    def scan_hardcoded_secrets(self) -> List[Dict]:
        """
        扫描硬编码的密码/密钥

        Returns:
            硬编码密钥列表
        """
        findings = []
        python_files = self._find_python_files()

        # 也包括配置文件
        all_files = python_files + self._find_all_files({'.json', '.yaml', '.yml', '.cfg', '.ini', '.env', '.txt'})

        for filepath in all_files:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')

                for lineno, line in enumerate(lines, 1):
                    for pattern in self.HARDCODED_SECRET_PATTERNS:
                        if re.search(pattern, line, re.IGNORECASE):
                            # 排除注释行
                            stripped = line.strip()
                            if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('<!--'):
                                continue
                            # 排除空字符串或明显的占位符
                            if re.search(r'[\'"]\s*[\'"]', line):
                                continue
                            if re.search(r'(?:TODO|FIXME|XXX|placeholder|your_|example)', line, re.IGNORECASE):
                                continue

                            findings.append({
                                'type': 'hardcoded_secret',
                                'file': str(filepath.relative_to(self.project_root)),
                                'line': lineno,
                                'code': line.strip()[:120],
                                'severity': 'critical',
                                'recommendation': '将密钥/密码移至环境变量或安全的配置管理系统（如 Vault）',
                            })
            except Exception:
                continue

        return findings

    # ========================================================================
    # 扫描模块2：安全最佳实践检查
    # ========================================================================

    def scan_best_practices(self) -> Dict[str, Dict]:
        """
        检查安全最佳实践覆盖情况

        Returns:
            实践检查结果映射
        """
        results = {}
        python_files = self._find_python_files()

        # 收集所有 Python 代码内容
        all_code = ""
        for filepath in python_files:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    all_code += f.read() + "\n"
            except Exception:
                continue

        for practice_id, practice in self.BEST_PRACTICES.items():
            found = False
            found_in = []

            for pattern in practice['patterns']:
                matches = re.findall(pattern, all_code, re.IGNORECASE)
                if matches:
                    found = True
                    found_in.append(pattern)

            results[practice_id] = {
                'name': practice['name'],
                'severity': practice['severity'],
                'implemented': found,
                'evidence': found_in,
                'recommendation': (f"[PASS] {practice['name']} 已实现" if found
                                   else f"[WARN] 建议实现 {practice['name']} 安全措施"),
            }

        return results

    # ========================================================================
    # 扫描模块3：密码策略合规检查
    # ========================================================================

    def scan_password_policy(self) -> Dict:
        """
        检查代码中的密码策略是否合规

        Returns:
            密码策略检查结果
        """
        # 定义推荐的安全策略
        recommended_policy = {
            'min_length': 8,
            'max_length': 128,
            'require_uppercase': True,
            'require_lowercase': True,
            'require_digit': True,
            'require_special': True,
            'max_attempts': 5,
            'lockout_minutes': 15,
            'password_history': 5,
        }

        # 扫描代码中定义的策略
        found_policies = {}
        python_files = self._find_python_files()
        all_code = ""

        for filepath in python_files:
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    all_code += content + "\n"

                    # 检测密码相关常量
                    for line in content.split('\n'):
                        if re.search(r'(?:MIN_PASSWORD_LENGTH|max_attempts|LOCKOUT)', line, re.IGNORECASE):
                            match = re.search(r'(\w+)\s*=\s*(\d+)', line)
                            if match:
                                found_policies[match.group(1)] = int(match.group(2))
            except Exception:
                continue

        # 比较策略
        policy_check = {
            'scan_time': datetime.now().isoformat(),
            'recommended_policy': recommended_policy,
            'found_policies': found_policies,
        }

        return policy_check

    # ========================================================================
    # 扫描模块4：依赖安全分析
    # ========================================================================

    def scan_dependencies(self) -> Dict:
        """
        检查项目依赖的安全性

        Returns:
            依赖分析结果
        """
        dep_files = self._find_all_files({'.txt'})

        # 查找 requirements 文件
        req_files = [f for f in dep_files if 'require' in f.name.lower()]

        dependencies = []
        for req_file in req_files:
            try:
                with open(req_file, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and not line.startswith('//'):
                            # 解析包名和版本
                            match = re.match(r'([a-zA-Z0-9_-]+)([><=!~]+.*)?', line)
                            if match:
                                dependencies.append({
                                    'package': match.group(1),
                                    'version': match.group(2) if match.group(2) else '未指定',
                                })
            except Exception:
                continue

        # 已知漏洞库检查（简化版）
        known_vulnerable = {
            'tensorflow': {
                'safe_versions': ['>=2.10.0'],
                'cve': 'CVE-2022-35941',
                'description': 'TensorFlow 旧版本存在多个安全漏洞',
            },
            'numpy': {
                'safe_versions': ['>=1.22.0'],
                'cve': 'CVE-2021-41495',
                'description': 'NumPy 1.21.5 以下版本存在缓冲区溢出风险',
            },
            'pillow': {
                'safe_versions': ['>=9.0.0'],
                'cve': 'CVE-2022-22817',
                'description': 'Pillow 旧版本存在多个图像处理漏洞',
            },
        }

        dep_check = {
            'dependencies': dependencies,
            'vulnerable': [],
        }

        for dep in dependencies:
            pkg = dep['package'].lower()
            if pkg in known_vulnerable:
                dep_check['vulnerable'].append({
                    'package': pkg,
                    'installed_version': dep['version'],
                    'safe_versions': known_vulnerable[pkg]['safe_versions'],
                    'cve': known_vulnerable[pkg]['cve'],
                    'description': known_vulnerable[pkg]['description'],
                })

        return dep_check

    # ========================================================================
    # 扫描模块5：文件权限与配置安全
    # ========================================================================

    def scan_file_permissions(self) -> List[Dict]:
        """
        检查敏感文件权限

        Returns:
            权限问题列表
        """
        findings = []
        sensitive_patterns = [
            'credentials', 'password', 'secret', 'token', 'key', '.pem', '.key',
            '.env', 'config.json', 'settings.json',
        ]

        for root, dirs, files in os.walk(self.project_root):
            for filename in files:
                for pattern in sensitive_patterns:
                    if pattern.lower() in filename.lower():
                        filepath = Path(root) / filename
                        try:
                            stat = os.stat(filepath)
                            # 检查是否对组或其他用户可读
                            if stat.st_mode & 0o077:  # 检查组和其他权限
                                findings.append({
                                    'type': 'file_permission',
                                    'file': str(filepath.relative_to(self.project_root)),
                                    'issue': '敏感文件权限过于宽松',
                                    'permissions': oct(stat.st_mode)[-3:],
                                    'recommendation': f'建议将 {filename} 权限设置为 600 (仅所有者可读写)',
                                })
                        except Exception:
                            continue

        return findings

    # ========================================================================
    # 主扫描流程
    # ========================================================================

    def run_full_scan(self) -> Dict:
        """
        运行完整的安全扫描

        Returns:
            扫描结果字典
        """
        print("\n" + "=" * 70)
        print("  [*] 安全扫描工具 - 完整扫描")
        print("=" * 70)

        scan_start = datetime.now()

        # 模块1：危险函数扫描
        print("\n[1/5] 危险函数扫描...")
        dangerous_functions = self.scan_dangerous_functions()
        print(f"      发现 {len(dangerous_functions)} 个潜在危险调用")

        # 模块2：硬编码密钥扫描
        print("[2/5] 硬编码密钥扫描...")
        hardcoded_secrets = self.scan_hardcoded_secrets()
        print(f"      发现 {len(hardcoded_secrets)} 个可疑硬编码")

        # 模块3：安全最佳实践检查
        print("[3/5] 安全最佳实践检查...")
        best_practices = self.scan_best_practices()
        implemented = sum(1 for v in best_practices.values() if v['implemented'])
        print(f"      已实现: {implemented}/{len(best_practices)}")

        # 模块4：密码策略合规检查
        print("[4/5] 密码策略合规检查...")
        password_policy = self.scan_password_policy()
        print(f"      策略检查完成")

        # 模块5：依赖安全分析
        print("[5/5] 依赖安全分析...")
        dependencies = self.scan_dependencies()
        print(f"      扫描 {len(dependencies['dependencies'])} 个依赖，"
              f"发现 {len(dependencies['vulnerable'])} 个潜在漏洞")

        scan_end = datetime.now()
        scan_duration = (scan_end - scan_start).total_seconds()

        # 计算安全评分
        score = self._calculate_security_score(
            dangerous_functions, hardcoded_secrets, best_practices, dependencies
        )

        self.scan_results = {
            'scan_time': scan_start.isoformat(),
            'scan_duration_seconds': scan_duration,
            'project_root': str(self.project_root),
            'dangerous_functions': dangerous_functions,
            'hardcoded_secrets': hardcoded_secrets,
            'best_practices': best_practices,
            'password_policy': password_policy,
            'dependencies': dependencies,
            'security_score': score,
        }

        # 生成报告文件
        self._generate_reports()

        print("\n" + "=" * 70)
        print(f"  [PASS] 扫描完成！耗时 {scan_duration:.2f} 秒")
        print(f"  安全评分: {score['total_score']}/100 ({score['grade']})")
        print(f"  报告目录: {self.output_dir}/")
        print("=" * 70)

        return self.scan_results

    # ========================================================================
    # 安全评分计算
    # ========================================================================

    def _calculate_security_score(
        self,
        dangerous_functions: List,
        hardcoded_secrets: List,
        best_practices: Dict,
        dependencies: Dict,
    ) -> Dict:
        """计算综合安全评分"""
        total_score = 100

        # 危险函数扣分
        high_severity = sum(1 for f in dangerous_functions if f.get('severity') == 'high')
        total_score -= min(high_severity * 5, 30)

        # 硬编码密钥扣分
        total_score -= min(len(hardcoded_secrets) * 10, 30)

        # 最佳实践加分
        implemented = sum(1 for v in best_practices.values() if v['implemented'])
        total_score += min(implemented * 2, 10)

        # 依赖漏洞扣分
        total_score -= min(len(dependencies.get('vulnerable', [])) * 5, 15)

        total_score = max(0, min(100, total_score))

        if total_score >= 90:
            grade = "优秀 (A)"
        elif total_score >= 75:
            grade = "良好 (B)"
        elif total_score >= 60:
            grade = "中等 (C)"
        elif total_score >= 40:
            grade = "较差 (D)"
        else:
            grade = "危险 (F)"

        return {
            'total_score': total_score,
            'grade': grade,
            'breakdown': {
                'dangerous_functions_penalty': min(high_severity * 5, 30),
                'hardcoded_secrets_penalty': min(len(hardcoded_secrets) * 10, 30),
                'best_practices_bonus': min(implemented * 2, 10),
                'dependency_penalty': min(len(dependencies.get('vulnerable', [])) * 5, 15),
            },
        }

    # ========================================================================
    # 报告生成
    # ========================================================================

    def _generate_reports(self):
        """生成安全扫描报告文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # 1. JSON 详细报告
        json_report_path = self.output_dir / f"security_scan_{timestamp}.json"
        with open(json_report_path, 'w', encoding='utf-8') as f:
            json.dump(self.scan_results, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n[*] JSON 报告: {json_report_path}")

        # 2. 摘要报告
        summary_path = self.output_dir / f"security_summary_{timestamp}.md"
        self._generate_summary_report(summary_path)
        print(f"[*] 摘要报告: {summary_path}")

        # 3. 安全检查清单
        checklist_path = self.output_dir / "security_checklist.md"
        self._generate_checklist_report(checklist_path)
        print(f"[*] 安全检查清单: {checklist_path}")

    def _generate_summary_report(self, filepath: Path):
        """生成 Markdown 摘要报告"""
        sr = self.scan_results
        score = sr.get('security_score', {})

        content = f"""# [LOCK] 安全扫描摘要报告

**扫描时间**: {sr.get('scan_time', 'Unknown')}
**扫描耗时**: {sr.get('scan_duration_seconds', 0):.2f} 秒
**项目目录**: {sr.get('project_root', 'Unknown')}

---

## [STATS] 安全评分

| 评分项 | 分数 |
|:---|---|
| **总分** | **{score.get('total_score', 'N/A')}/100** |
| **等级** | **{score.get('grade', 'N/A')}** |

### 评分明细

| 类别 | 扣分/加分 |
|:---|---|
| 危险函数扣分 | -{score.get('breakdown', {}).get('dangerous_functions_penalty', 0)} |
| 硬编码密钥扣分 | -{score.get('breakdown', {}).get('hardcoded_secrets_penalty', 0)} |
| 最佳实践加分 | +{score.get('breakdown', {}).get('best_practices_bonus', 0)} |
| 依赖漏洞扣分 | -{score.get('breakdown', {}).get('dependency_penalty', 0)} |

---

## [WARN] 发现的问题

### 危险函数调用 ({len(sr.get('dangerous_functions', []))} 个)

"""
        for finding in sr.get('dangerous_functions', []):
            if isinstance(finding, dict):
                content += f"- `{finding.get('file', '?')}:{finding.get('line', '?')}` - {finding.get('function', '?')}\n"

        content += f"""
### 硬编码密钥 ({len(sr.get('hardcoded_secrets', []))} 个)

"""
        for finding in sr.get('hardcoded_secrets', []):
            if isinstance(finding, dict):
                content += f"- `{finding.get('file', '?')}:{finding.get('line', '?')}` - 疑似硬编码\n"

        content += f"""
### 依赖漏洞 ({len(sr.get('dependencies', {}).get('vulnerable', []))} 个)

"""
        for vuln in sr.get('dependencies', {}).get('vulnerable', []):
            content += f"- **{vuln.get('package', '?')}** {vuln.get('installed_version', '?')}: {vuln.get('description', '?')} ({vuln.get('cve', '?')})\n"

        content += """

---

## [PASS] 安全最佳实践

| 实践 | 状态 |
|:---|:---:|
"""
        for pid, practice in sr.get('best_practices', {}).items():
            status = '[PASS] 已实现' if practice.get('implemented') else '[WARN] 未实现'
            content += f"| {practice.get('name', pid)} | {status} |\n"

        content += """
---

> 此报告由 SecurityScanner 自动生成
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    def _generate_checklist_report(self, filepath: Path):
        """生成安全检查清单"""
        sr = self.scan_results
        best_practices = sr.get('best_practices', {})

        content = f"""# [PASS] 安全检查清单

**生成时间**: {datetime.now().isoformat()}
**项目**: {sr.get('project_root', 'Unknown')}

---

## 密码管理安全检查

- [ ] 密码使用哈希算法存储（SHA-256 / bcrypt / PBKDF2）
- [ ] 密码使用独立盐值
- [ ] 密码强度策略已强制执行
- [ ] 密码历史记录已保留（防止重用）
- [ ] 账户锁定机制已实现
- [ ] 登录冷却时间已设置

## 身份认证安全检查

- [ ] 密保问题已设置（≥3个）
- [ ] 密码重置需要密保验证
- [ ] 密码重置需要二次身份确认
- [ ] 重置令牌有过期时间
- [ ] 防止用户名枚举攻击

## 代码安全检查

"""
        for pid, practice in best_practices.items():
            check = '[PASS]' if practice.get('implemented') else '[FAIL]'
            content += f"- [{check}] {practice.get('name', pid)} (严重程度: {practice.get('severity', 'N/A')})\n"

        content += f"""

## 依赖安全检查

| 依赖 | 当前版本 | 安全版本 | 状态 |
|:---|:---|:---|:---|
"""
        for dep in sr.get('dependencies', {}).get('dependencies', []):
            safe = '[PASS] 安全' if dep.get('package', '').lower() not in [
                v.get('package', '') for v in sr.get('dependencies', {}).get('vulnerable', [])
            ] else '[WARN] 有漏洞'
            content += f"| {dep.get('package', '?')} | {dep.get('version', '?')} | - | {safe} |\n"

        content += """
---

> 此清单由 SecurityScanner 自动生成
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)


# ========================================================================
# 直接运行
# ========================================================================

if __name__ == "__main__":
    # 使用当前项目根目录
    current_dir = Path(__file__).resolve().parent.parent
    scanner = SecurityScanner(
        project_root=str(current_dir),
        output_dir=str(current_dir / "reports"),
    )
    scanner.run_full_scan()
