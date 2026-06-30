"""
密码管理模块 (Password Manager)
================================
功能：
 - 用户注册（含密保问题设置）
 - 密码哈希存储（SHA-256 + 盐值）
 - 密保问题验证
 - 密码重置流程（含二次身份确认）
 - 登录尝试限制与账户锁定
 - 密码强度评估

安全控制点：
 - 密码重置逻辑验证（密保问题 + 二次确认码）
 - 二次身份确认（邮箱验证码模拟）
 - 暴力破解防护（登录尝试限制）
 - 密码强度策略强制执行
"""

import sys
# 确保 Windows 控制台支持 UTF-8 输出
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import hashlib
import secrets
import string
import re
import json
import os
import time
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, List


class PasswordManager:
    """密码管理器：处理用户注册、登录、密码重置与安全验证"""

    # ========================================================================
    # 配置常量
    # ========================================================================

    # 密码策略
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 128
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    SPECIAL_CHARS = "!@#$%^&*()-_=+[]{}|;:,.<>?/~`"

    # 登录安全
    MAX_LOGIN_ATTEMPTS = 5                # 最大尝试次数
    LOCKOUT_DURATION_MINUTES = 15         # 锁定时间（分钟）
    LOCKOUT_COOLDOWN_SECONDS = 2          # 失败后冷却时间（秒）

    # 密码重置
    RESET_CODE_LENGTH = 6                 # 重置验证码长度
    RESET_CODE_EXPIRY_MINUTES = 5         # 重置验证码有效期（分钟）
    MIN_SECURITY_QUESTIONS = 3            # 最少密保问题数量
    REQUIRED_CORRECT_ANSWERS = 2          # 重置时需要答对的密保问题数

    # 预置密保问题库
    DEFAULT_SECURITY_QUESTIONS = [
        "您的出生地是哪里？",
        "您的小学校名是什么？",
        "您母亲的名字是什么？",
        "您父亲的名字是什么？",
        "您最喜欢的宠物名字是什么？",
        "您第一辆车的品牌是什么？",
        "您最喜欢的书籍名称是什么？",
        "您最喜欢的电影名称是什么？",
        "您最尊敬的老师的名字是什么？",
        "您童年最好的朋友叫什么名字？",
    ]

    def __init__(self, storage_path: str = "user_credentials.json"):
        """
        初始化密码管理器

        Args:
            storage_path: 用户凭证存储文件路径
        """
        self.storage_path = storage_path
        self.users: Dict = {}                    # 用户数据
        self.login_attempts: Dict[str, int] = {} # 登录尝试计数
        self.lockout_records: Dict[str, float] = {}  # 锁定记录
        self.reset_codes: Dict[str, Dict] = {}   # 重置验证码
        self._load_users()

    # ========================================================================
    # 数据持久化
    # ========================================================================

    def _load_users(self) -> None:
        """从文件加载用户数据"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
                print(f"[密码管理器] 已加载 {len(self.users)} 个用户账户")
            except (json.JSONDecodeError, IOError) as e:
                print(f"[密码管理器] 警告：加载用户数据失败 ({e})，使用空数据库")
                self.users = {}
        else:
            print("[密码管理器] 未找到用户数据文件，初始化空数据库")

    def _save_users(self) -> None:
        """持久化用户数据到文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.storage_path) if os.path.dirname(self.storage_path) else '.', exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"[密码管理器] 错误：保存用户数据失败 ({e})")

    # ========================================================================
    # 密码哈希与验证
    # ========================================================================

    @staticmethod
    def _generate_salt(length: int = 32) -> str:
        """生成随机盐值"""
        return secrets.token_hex(length)

    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        """
        使用 SHA-256 + 盐值进行密码哈希

        Args:
            password: 明文密码
            salt: 盐值

        Returns:
            十六进制哈希字符串
        """
        # 使用 PBKDF2 风格的迭代哈希（增强抗暴力破解能力）
        iterations = 100_000
        data = (password + salt).encode('utf-8')
        for _ in range(iterations):
            data = hashlib.sha256(data).digest()
        return data.hex()

    @staticmethod
    def evaluate_password_strength(password: str) -> Tuple[int, str, List[str]]:
        """
        评估密码强度

        Args:
            password: 明文密码

        Returns:
            (分数 0-100, 等级, 建议列表)
        """
        score = 0
        suggestions = []

        # 长度评分
        length = len(password)
        if length >= 16:
            score += 30
        elif length >= 12:
            score += 20
        elif length >= 8:
            score += 10
        else:
            suggestions.append("密码长度应至少为8个字符")

        # 字符多样性
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'[0-9]', password))
        has_special = bool(re.search(r'[^A-Za-z0-9]', password))

        diversity_count = sum([has_upper, has_lower, has_digit, has_special])
        score += diversity_count * 10

        if not has_upper:
            suggestions.append("建议包含大写字母")
        if not has_lower:
            suggestions.append("建议包含小写字母")
        if not has_digit:
            suggestions.append("建议包含数字")
        if not has_special:
            suggestions.append("建议包含特殊字符")

        # 模式检测（扣分项）
        if re.search(r'(.)\1{2,}', password):
            score -= 10
            suggestions.append("避免连续重复字符")

        if re.search(r'(?:abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):
            score -= 10
            suggestions.append("避免连续字母序列")

        if re.search(r'(?:012|123|234|345|456|567|678|789|890)', password):
            score -= 10
            suggestions.append("避免连续数字序列")

        # 常见密码检测
        common_patterns = [
            r'password', r'123456', r'qwerty', r'admin',
            r'letmein', r'welcome', r'monkey', r'dragon',
        ]
        for pattern in common_patterns:
            if re.search(pattern, password.lower()):
                score -= 20
                suggestions.append(f"避免使用常见密码模式 '{pattern}'")
                break

        # 最终评分
        score = max(0, min(100, score))

        # 等级评定
        if score >= 80:
            grade = "很强 🔒"
        elif score >= 60:
            grade = "强 ✅"
        elif score >= 40:
            grade = "中等 ⚠️"
        elif score >= 20:
            grade = "弱 ❌"
        else:
            grade = "非常弱 🚫"

        return score, grade, suggestions

    # ========================================================================
    # 用户注册
    # ========================================================================

    def register_user(
        self,
        username: str,
        password: str,
        security_questions: Dict[str, str],
        email: str = "",
    ) -> Tuple[bool, str]:
        """
        注册新用户（含密保问题设置）

        Args:
            username: 用户名
            password: 明文密码
            security_questions: 密保问题与答案字典 {问题: 答案}
            email: 邮箱（用于二次身份确认）

        Returns:
            (成功标志, 消息)
        """
        # 验证用户名
        if not username or not username.strip():
            return False, "❌ 用户名不能为空"

        username = username.strip().lower()
        if username in self.users:
            return False, f"❌ 用户名 '{username}' 已被注册"

        if len(username) < 3:
            return False, "❌ 用户名长度至少为3个字符"
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "❌ 用户名只能包含字母、数字和下划线"

        # 验证密码强度
        score, grade, suggestions = self.evaluate_password_strength(password)
        if score < 40:
            return False, f"❌ 密码强度不足（等级：{grade}）。建议：{'; '.join(suggestions)}"

        # 验证密保问题
        if len(security_questions) < self.MIN_SECURITY_QUESTIONS:
            return False, f"❌ 至少需要设置 {self.MIN_SECURITY_QUESTIONS} 个密保问题，当前仅 {len(security_questions)} 个"

        # 验证密保答案不为空
        for question, answer in security_questions.items():
            if not answer or not answer.strip():
                return False, f"❌ 密保问题 '{question}' 的答案不能为空"

        # 哈希密码
        salt = self._generate_salt()
        password_hash = self._hash_password(password, salt)

        # 哈希密保答案（每个答案独立加盐哈希）
        hashed_questions = {}
        for question, answer in security_questions.items():
            ans_salt = self._generate_salt()
            ans_hash = self._hash_password(answer.strip().lower(), ans_salt)
            hashed_questions[question] = {
                'hash': ans_hash,
                'salt': ans_salt,
            }

        # 存储用户
        self.users[username] = {
            'password_hash': password_hash,
            'password_salt': salt,
            'security_questions': hashed_questions,
            'email': email,
            'created_at': datetime.now().isoformat(),
            'last_password_change': datetime.now().isoformat(),
            'password_history': [password_hash],  # 密码历史，防止重用
            'login_attempts': 0,
            'is_locked': False,
            'lockout_until': None,
        }

        self._save_users()
        self.login_attempts[username] = 0

        print(f"\n✅ 用户 '{username}' 注册成功！")
        print(f"   密码强度：{grade} ({score}/100)")
        print(f"   密保问题：已设置 {len(security_questions)} 个")
        return True, f"✅ 用户 '{username}' 注册成功"

    # ========================================================================
    # 用户登录
    # ========================================================================

    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """
        用户登录（含账户锁定保护）

        Args:
            username: 用户名
            password: 明文密码

        Returns:
            (成功标志, 消息)
        """
        username = username.strip().lower()

        # 检查用户是否存在
        if username not in self.users:
            # 防止用户名枚举攻击：使用相同的延时
            time.sleep(0.5)
            return False, "❌ 用户名或密码错误"

        user = self.users[username]

        # 检查账户是否被锁定
        if user.get('is_locked', False):
            lockout_until = user.get('lockout_until')
            if lockout_until:
                lockout_time = datetime.fromisoformat(lockout_until)
                if datetime.now() < lockout_time:
                    remaining = (lockout_time - datetime.now()).seconds
                    return False, f"🚫 账户已锁定，请在 {remaining} 秒后重试"
                else:
                    # 锁定期已过，自动解除
                    user['is_locked'] = False
                    user['lockout_until'] = None
                    user['login_attempts'] = 0
                    self._save_users()

        # 验证密码
        password_hash = self._hash_password(password, user['password_salt'])
        if password_hash == user['password_hash']:
            # 登录成功
            user['login_attempts'] = 0
            user['is_locked'] = False
            user['lockout_until'] = None
            self._save_users()
            print(f"\n✅ 用户 '{username}' 登录成功！")
            return True, f"✅ 欢迎回来，{username}！"

        # 登录失败
        user['login_attempts'] = user.get('login_attempts', 0) + 1
        remaining = self.MAX_LOGIN_ATTEMPTS - user['login_attempts']

        if user['login_attempts'] >= self.MAX_LOGIN_ATTEMPTS:
            # 锁定账户
            user['is_locked'] = True
            user['lockout_until'] = (datetime.now() + timedelta(minutes=self.LOCKOUT_DURATION_MINUTES)).isoformat()
            self._save_users()
            return False, f"🚫 登录尝试次数过多，账户已锁定 {self.LOCKOUT_DURATION_MINUTES} 分钟"

        self._save_users()
        time.sleep(self.LOCKOUT_COOLDOWN_SECONDS)  # 冷却延时防止暴力破解
        return False, f"❌ 用户名或密码错误（剩余尝试次数：{remaining}）"

    # ========================================================================
    # 密码重置流程（含安全控制点）
    # ========================================================================

    def initiate_password_reset(self, username: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        发起密码重置请求

        安全控制点1：密保问题验证

        Args:
            username: 用户名

        Returns:
            (成功标志, 消息, 密保问题列表)
        """
        username = username.strip().lower()

        if username not in self.users:
            # 防止用户名枚举
            time.sleep(0.5)
            return False, "如果该账户存在，密码重置流程已启动", None

        user = self.users[username]

        # 获取密保问题（随机抽取与展示）
        questions = list(user['security_questions'].keys())
        selected_questions = secrets.SystemRandom().sample(
            questions,
            min(len(questions), self.REQUIRED_CORRECT_ANSWERS)
        )

        return True, f"请回答以下密保问题以验证身份", {
            'username': username,
            'questions': selected_questions,
        }

    def verify_security_questions(
        self,
        username: str,
        answers: Dict[str, str]
    ) -> Tuple[bool, str, Optional[str]]:
        """
        验证密保问题答案

        Args:
            username: 用户名
            answers: 密保问题与答案映射

        Returns:
            (验证成功, 消息, 重置令牌)
        """
        username = username.strip().lower()

        if username not in self.users:
            return False, "❌ 身份验证失败", None

        user = self.users[username]
        stored_questions = user['security_questions']
        correct_count = 0

        for question, provided_answer in answers.items():
            if question not in stored_questions:
                continue

            stored_data = stored_questions[question]
            expected_hash = self._hash_password(
                provided_answer.strip().lower(),
                stored_data['salt']
            )

            if expected_hash == stored_data['hash']:
                correct_count += 1

        if correct_count >= self.REQUIRED_CORRECT_ANSWERS:
            # 密保问题验证通过 ✅
            # 生成密码重置令牌
            reset_token = secrets.token_urlsafe(32)
            self.reset_codes[reset_token] = {
                'username': username,
                'expires_at': (datetime.now() + timedelta(minutes=self.RESET_CODE_EXPIRY_MINUTES)).isoformat(),
            }
            return True, f"✅ 密保问题验证通过！({correct_count}/{len(answers)} 正确)", reset_token

        return False, f"❌ 密保验证失败（仅答对 {correct_count}/{len(answers)}，需要至少 {self.REQUIRED_CORRECT_ANSWERS} 个）", None

    def send_secondary_verification(self, username: str) -> Tuple[bool, str, Optional[str]]:
        """
        发送二次身份确认码（安全控制点2）

        模拟邮箱/手机验证码发送，实际部署时可集成 SMS/Email API

        Args:
            username: 用户名

        Returns:
            (成功标志, 消息, 验证码)
        """
        username = username.strip().lower()

        if username not in self.users:
            return False, "❌ 用户不存在", None

        # 生成6位数字验证码
        verification_code = ''.join(secrets.choice(string.digits) for _ in range(self.RESET_CODE_LENGTH))

        # 存储验证码
        user = self.users[username]
        user['_pending_verification_code'] = self._hash_password(verification_code, user['password_salt'])
        user['_verification_code_expiry'] = (datetime.now() + timedelta(minutes=self.RESET_CODE_EXPIRY_MINUTES)).isoformat()
        self._save_users()

        # 模拟发送（实际应用中通过邮件/SMS发送）
        email = user.get('email', '未设置邮箱')
        print(f"\n📧 === 二次身份确认（模拟）===")
        print(f"   收件人: {email}")
        print(f"   验证码: {verification_code}")
        print(f"   有效期: {self.RESET_CODE_EXPIRY_MINUTES} 分钟")
        print(f"   ============================\n")

        return True, f"验证码已发送至 {email}", verification_code

    def verify_secondary_code(
        self,
        username: str,
        code: str
    ) -> Tuple[bool, str]:
        """
        验证二次身份确认码

        Args:
            username: 用户名
            code: 验证码

        Returns:
            (验证成功, 消息)
        """
        username = username.strip().lower()

        if username not in self.users:
            return False, "❌ 验证失败"

        user = self.users[username]

        # 检查验证码是否过期
        expiry = user.get('_verification_code_expiry')
        if expiry and datetime.now() > datetime.fromisoformat(expiry):
            return False, "❌ 验证码已过期，请重新发送"

        # 验证验证码
        expected_hash = self._hash_password(code, user['password_salt'])
        if expected_hash != user.get('_pending_verification_code', ''):
            return False, "❌ 验证码错误"

        # 清理验证码
        user.pop('_pending_verification_code', None)
        user.pop('_verification_code_expiry', None)
        self._save_users()

        return True, "✅ 二次身份确认成功"

    def reset_password(
        self,
        username: str,
        new_password: str,
        reset_token: str,
        secondary_code: str,
    ) -> Tuple[bool, str]:
        """
        执行密码重置（完整安全流程）

        安全控制点：
        1. 密保问题验证（通过 reset_token 确认已完成）
        2. 二次身份确认码验证
        3. 新密码强度检查
        4. 密码历史检查（防止重用）

        Args:
            username: 用户名
            new_password: 新密码
            reset_token: 密保验证通过后获取的重置令牌
            secondary_code: 二次确认验证码

        Returns:
            (成功标志, 消息)
        """
        username = username.strip().lower()

        # 安全控制点1：验证重置令牌
        if reset_token not in self.reset_codes:
            return False, "❌ 无效的重置令牌，请重新发起密码重置"

        token_data = self.reset_codes[reset_token]
        if token_data['username'] != username:
            return False, "❌ 重置令牌与用户不匹配"

        if datetime.now() > datetime.fromisoformat(token_data['expires_at']):
            del self.reset_codes[reset_token]
            return False, "❌ 重置令牌已过期，请重新发起密码重置"

        # 安全控制点2：二次身份确认
        success, msg = self.verify_secondary_code(username, secondary_code)
        if not success:
            return False, f"❌ 二次身份确认失败：{msg}"

        if username not in self.users:
            return False, "❌ 用户不存在"

        user = self.users[username]

        # 安全控制点3：新密码强度检查
        score, grade, suggestions = self.evaluate_password_strength(new_password)
        if score < 40:
            return False, f"❌ 新密码强度不足（等级：{grade}）。建议：{'; '.join(suggestions)}"

        # 安全控制点4：密码历史检查（防止密码重用）
        for old_hash in user.get('password_history', []):
            new_hash = self._hash_password(new_password, user['password_salt'])
            if new_hash == old_hash:
                return False, "❌ 新密码不能与历史密码相同"

        # 生成新的盐值并更新密码
        new_salt = self._generate_salt()
        new_password_hash = self._hash_password(new_password, new_salt)

        user['password_hash'] = new_password_hash
        user['password_salt'] = new_salt
        user['last_password_change'] = datetime.now().isoformat()
        user['password_history'] = user.get('password_history', [])[-4:]  # 保留最近5个
        user['password_history'].append(new_password_hash)
        user['is_locked'] = False
        user['login_attempts'] = 0
        user['lockout_until'] = None

        self._save_users()

        # 清理重置令牌
        del self.reset_codes[reset_token]

        print(f"\n✅ 用户 '{username}' 密码重置成功！")
        print(f"   新密码强度：{grade} ({score}/100)")
        return True, f"✅ 密码重置成功！请使用新密码登录"

    # ========================================================================
    # 账户状态查询
    # ========================================================================

    def get_account_status(self, username: str) -> Optional[Dict]:
        """
        获取账户安全状态

        Args:
            username: 用户名

        Returns:
            账户状态字典
        """
        username = username.strip().lower()
        if username not in self.users:
            return None

        user = self.users[username]
        return {
            'username': username,
            'created_at': user.get('created_at', '未知'),
            'last_password_change': user.get('last_password_change', '未知'),
            'is_locked': user.get('is_locked', False),
            'login_attempts': user.get('login_attempts', 0),
            'security_questions_count': len(user.get('security_questions', {})),
            'has_email': bool(user.get('email', '')),
        }

    # ========================================================================
    # 交互式演示
    # ========================================================================

    @classmethod
    def run_interactive_demo(cls):
        """
        运行交互式密码管理演示
        展示完整的注册 → 登录 → 密码重置流程
        """
        pm = cls(storage_path="reports/user_credentials.json")

        print("\n" + "=" * 70)
        print("  🔐 密码管理系统 - 交互式演示")
        print("  安全控制点：密保验证 + 二次身份确认 + 密码策略")
        print("=" * 70)

        while True:
            print("\n" + "-" * 50)
            print("请选择操作：")
            print("  1. 注册新用户")
            print("  2. 用户登录")
            print("  3. 密码重置")
            print("  4. 查看账户状态")
            print("  5. 退出")
            print("-" * 50)
            choice = input("请输入选项 (1-5): ").strip()

            if choice == '1':
                cls._demo_register(pm)
            elif choice == '2':
                cls._demo_login(pm)
            elif choice == '3':
                cls._demo_reset_password(pm)
            elif choice == '4':
                cls._demo_account_status(pm)
            elif choice == '5':
                print("\n👋 感谢使用密码管理系统！")
                break
            else:
                print("❌ 无效选项，请重新选择")

    @staticmethod
    def _demo_register(pm: 'PasswordManager'):
        """演示用户注册"""
        print("\n--- 📝 用户注册 ---")
        username = input("请输入用户名: ").strip()
        password = input("请输入密码: ").strip()

        # 选择密保问题
        print("\n请选择密保问题（至少3个）：")
        for i, q in enumerate(pm.DEFAULT_SECURITY_QUESTIONS, 1):
            print(f"  {i}. {q}")

        security_questions = {}
        while len(security_questions) < pm.MIN_SECURITY_QUESTIONS:
            choice = input(f"请选择密保问题编号 (当前已选 {len(security_questions)}/{pm.MIN_SECURITY_QUESTIONS}): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(pm.DEFAULT_SECURITY_QUESTIONS):
                    question = pm.DEFAULT_SECURITY_QUESTIONS[idx]
                    if question in security_questions:
                        print("⚠️ 该问题已选择，请选择其他问题")
                        continue
                    answer = input(f"请输入答案 [{question}]: ").strip()
                    if answer:
                        security_questions[question] = answer
                    else:
                        print("⚠️ 答案不能为空")
                else:
                    print("❌ 无效的问题编号")
            except ValueError:
                print("❌ 请输入数字编号")

        email = input("请输入邮箱（用于二次身份确认）: ").strip()

        success, msg = pm.register_user(username, password, security_questions, email)
        print(msg)

    @staticmethod
    def _demo_login(pm: 'PasswordManager'):
        """演示用户登录"""
        print("\n--- 🔑 用户登录 ---")
        username = input("请输入用户名: ").strip()
        password = input("请输入密码: ").strip()
        success, msg = pm.login(username, password)
        print(msg)

    @staticmethod
    def _demo_reset_password(pm: 'PasswordManager'):
        """演示密码重置完整流程（含所有安全控制点）"""
        print("\n--- 🔄 密码重置（含安全控制点验证）---")
        username = input("请输入要重置密码的用户名: ").strip()

        # 步骤1：发起密码重置
        print("\n[安全控制点1/3] 密保问题验证")
        success, msg, data = pm.initiate_password_reset(username)
        print(msg)

        if not success or data is None:
            return

        # 步骤2：回答密保问题
        answers = {}
        for question in data['questions']:
            answer = input(f"请回答 - {question}: ").strip()
            if answer:
                answers[question] = answer

        success, msg, reset_token = pm.verify_security_questions(username, answers)
        print(msg)

        if not success or reset_token is None:
            return

        # 步骤3：二次身份确认
        print("\n[安全控制点2/3] 二次身份确认")
        success, msg, code = pm.send_secondary_verification(username)
        print(msg)

        if not success:
            return

        user_code = input("请输入收到的验证码: ").strip()
        success, msg = pm.verify_secondary_code(username, user_code)
        print(msg)

        if not success:
            return

        # 步骤4：设置新密码
        print("\n[安全控制点3/3] 新密码设置与策略检查")
        new_password = input("请输入新密码: ").strip()

        # 使用已获取的验证码作为 secondary_code（跳过重新发送）
        success, msg = pm.reset_password(username, new_password, reset_token, user_code)
        print(msg)

    @staticmethod
    def _demo_account_status(pm: 'PasswordManager'):
        """演示账户状态查询"""
        print("\n--- 📊 账户安全状态 ---")
        username = input("请输入用户名: ").strip()
        status = pm.get_account_status(username)
        if status:
            print(f"\n用户名: {status['username']}")
            print(f"创建时间: {status['created_at']}")
            print(f"最后密码修改: {status['last_password_change']}")
            print(f"账户状态: {'🚫 已锁定' if status['is_locked'] else '✅ 正常'}")
            print(f"登录尝试次数: {status['login_attempts']}")
            print(f"密保问题数量: {status['security_questions_count']}")
            print(f"是否设置邮箱: {'是' if status['has_email'] else '否'}")
        else:
            print(f"❌ 用户 '{username}' 不存在")


# ========================================================================
# 直接运行演示
# ========================================================================

if __name__ == "__main__":
    PasswordManager.run_interactive_demo()
