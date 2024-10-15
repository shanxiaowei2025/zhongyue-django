from django.db import models
from django.utils import timezone

class Customer(models.Model):
    ENTERPRISE_STATUS_CHOICES = [
        ('active', '正常'),
        ('suspended', '已注销'),
        ('closed', '已流失'),
    ]

    TAX_REGISTRATION_CHOICES = [
        ('general', '一般纳税人'),
        ('small_scale', '小规模纳税人'),
    ]

    BUSINESS_STATUS_CHOICES = [
        ('ongoing', '进行中'),
        ('completed', '已完成'),
        ('suspended', '已暂停'),
    ]

    company_name = models.CharField(max_length=255, verbose_name="企业名称", help_text="企业的法定名称", db_comment="企业的法定名称", blank=True, null=True)
    daily_contact = models.CharField(max_length=100, verbose_name="日常业务联系人", help_text="日常业务联系人姓名", db_comment="日常业务联系人姓名", blank=True, null=True)
    daily_contact_phone = models.CharField(max_length=20, verbose_name="日常客户联系人电话", help_text="日常业务联系人的联系电话", db_comment="日常业务联系人的联系电话", blank=True, null=True)
    sales_representative = models.CharField(max_length=100, verbose_name="业务员", help_text="负责该客户的业务员姓名", db_comment="负责该客户的业务员姓名", blank=True, null=True)
    social_credit_code = models.CharField(max_length=18, verbose_name="统一社会信用代码", help_text="企业的统一社会信用代码", db_comment="企业的统一社会信用代码", blank=True, null=True)
    tax_bureau = models.CharField(max_length=100, verbose_name="所属分局", help_text="企业所属的税务分局", db_comment="企业所属的税务分局", blank=True, null=True)
    business_source = models.CharField(max_length=100, verbose_name="业务来源", help_text="客户的业务来源渠道", db_comment="客户的业务来源渠道", blank=True, null=True)
    tax_registration_type = models.CharField(max_length=20, choices=TAX_REGISTRATION_CHOICES, verbose_name="税务登记类型", help_text="企业的税务登记类型", db_comment="企业的税务登记类型", blank=True, null=True)
    chief_accountant = models.CharField(max_length=100, verbose_name="主管会计", help_text="负责该企业的主管会计姓名", db_comment="负责该企业的主管会计姓名", blank=True, null=True)
    responsible_accountant = models.CharField(max_length=100, verbose_name="责任会计", help_text="负责该企业的责任会计姓名", db_comment="负责该企业的责任会计姓名", blank=True, null=True)
    enterprise_status = models.CharField(max_length=20, choices=ENTERPRISE_STATUS_CHOICES, verbose_name="企业状态", help_text="企业当前的经营状态", db_comment="企业当前的经营状态", blank=True, null=True)
    affiliated_enterprises = models.TextField(blank=True, verbose_name="同宗企业", help_text="与该企业有关联的其他企业", db_comment="与该企业有关联的其他企业", null=True)
    main_business = models.TextField(verbose_name="企业主营", help_text="企业的主要经营业务", db_comment="企业的主要经营业务", blank=True, null=True)
    boss_profile = models.TextField(blank=True, verbose_name="老板画像", help_text="企业老板的个人特征描述", db_comment="企业老板的个人特征描述", null=True)
    communication_notes = models.TextField(blank=True, verbose_name="沟通注意事项", help_text="与该企业沟通时需要注意的事项", db_comment="与该企业沟通时需要注意的事项", null=True)
    business_scope = models.TextField(verbose_name="经营范围", help_text="企业的经营范围描述", db_comment="企业的经营范围描述", blank=True, null=True)
    business_address = models.TextField(verbose_name="经营地址", help_text="企业的实际经营地址", db_comment="企业的实际经营地址", blank=True, null=True)
    registered_capital = models.DecimalField(max_digits=15, decimal_places=0, verbose_name="注册资本", help_text="企业的注册资本金额", db_comment="企业的注册资本金额", blank=True, null=True)
    establishment_date = models.DateField(verbose_name="成立时间", help_text="企业的成立日期", db_comment="企业的成立日期", blank=True, null=True)
    license_expiry_date = models.DateField(verbose_name="执照到期日", help_text="营业执照的到期日期", db_comment="营业执照的到期日期", blank=True, null=True)
    capital_contribution_deadline = models.DateField(verbose_name="认缴到期日", help_text="注册资本认缴的截止日期", db_comment="注册资本认缴的截止日期", blank=True, null=True)
    enterprise_type = models.CharField(max_length=100, verbose_name="企业类型", help_text="企业的类型，如有限责任公司、股份有限公司等", db_comment="企业的类型，如有限责任公司、股份有限公司等", blank=True, null=True)
    shareholders = models.TextField(verbose_name="股东", help_text="企业的股东信息", db_comment="企业的股东信息", blank=True, null=True)
    supervisors = models.TextField(verbose_name="监事", help_text="企业的监事信息", db_comment="企业的监事信息", blank=True, null=True)
    annual_inspection_password = models.CharField(max_length=100, verbose_name="工商年检密码", help_text="工商年检系统的登录密码", db_comment="工商年检系统的登录密码", blank=True, null=True)
    paid_in_capital = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="实缴金额", help_text="企业实际缴纳的注册资本金额", db_comment="企业实际缴纳的注册资本金额", blank=True, null=True)
    administrative_licenses = models.TextField(blank=True, verbose_name="行政许可", help_text="企业获得的行政许可信息", db_comment="企业获得的行政许可信息", null=True)
    capital_contribution_records = models.TextField(blank=True, verbose_name="实缴记录", help_text="企业注册资本实缴的记录", db_comment="企业注册资本实缴的记录", null=True)
    basic_bank = models.CharField(max_length=100, verbose_name="基本开户银行", help_text="企业的基本开户银行名称", db_comment="企业的基本开户银行名称", blank=True, null=True)
    basic_bank_account = models.CharField(max_length=30, verbose_name="基本开户行账号", help_text="企业的基本开户银行账号", db_comment="企业的基本开户银行账号", blank=True, null=True)
    basic_bank_number = models.CharField(max_length=20, verbose_name="基本开户行行号", help_text="企业基本开户银行的行号", db_comment="企业基本开户银行的行号", blank=True, null=True)
    general_bank = models.CharField(max_length=100, blank=True, verbose_name="一般开户行", help_text="企业的一般开户银行名称", db_comment="企业的一般开户银行名称", null=True)
    general_bank_account = models.CharField(max_length=30, blank=True, verbose_name="一般开户银行账号", help_text="企业的一般开户银行账号", db_comment="企业的一般开户银行账号", null=True)
    general_bank_number = models.CharField(max_length=20, blank=True, verbose_name="一般开户行行号", help_text="企业一般开户银行的行号", db_comment="企业一般开户银行的行号", null=True)
    has_online_banking = models.BooleanField(default=False, verbose_name="是否办理网银盾", help_text="企业是否办理了网上银行", db_comment="企业是否办理了网上银行")
    is_online_banking_custodian = models.BooleanField(default=False, verbose_name="是否网银盾托管", help_text="企业的网银盾是否由我方托管", db_comment="企业的网银盾是否由我方托管")
    legal_representative_name = models.CharField(max_length=100, verbose_name="法人姓名", help_text="企业法定代表人姓名", db_comment="企业法定代表人姓名", blank=True, null=True)
    legal_representative_phone = models.CharField(max_length=20, verbose_name="法人联系人电话", help_text="企业法定代表人的联系电话", db_comment="企业法定代表人的联系电话", blank=True, null=True)
    legal_representative_id = models.CharField(max_length=18, verbose_name="法人身份证", help_text="企业法定代表人的身份证号码", db_comment="企业法定代表人的身份证号码", blank=True, null=True)
    legal_representative_tax_password = models.CharField(max_length=100, verbose_name="法人电子税务局密码", help_text="法定代表人的电子税务局登录密码", db_comment="法定代表人的电子税务局登录密码", blank=True, null=True)
    financial_contact_name = models.CharField(max_length=100, verbose_name="财务负责人姓名", help_text="企业财务负责人姓名", db_comment="企业财务负责人姓名", blank=True, null=True)
    financial_contact_phone = models.CharField(max_length=20, verbose_name="财务负责人联系电话", help_text="企业财务负责人的联系电话", db_comment="企业财务负责人的联系电话", blank=True, null=True)
    financial_contact_id = models.CharField(max_length=18, verbose_name="财务负责人身份证", help_text="企业财务负责人的身份证号码", db_comment="企业财务负责人的身份证号码", blank=True, null=True)
    financial_contact_tax_password = models.CharField(max_length=100, verbose_name="财务负责人电子税务局密码", help_text="财务负责人的电子税务局登录密码", db_comment="财务负责人的电子税务局登录密码", blank=True, null=True)
    tax_officer_name = models.CharField(max_length=100, verbose_name="办税员姓名", help_text="企业办税员姓名", db_comment="企业办税员姓名", blank=True, null=True)
    tax_officer_phone = models.CharField(max_length=20, verbose_name="办税员联系电话", help_text="企业办税员的联系电话", db_comment="企业办税员的联系电话", blank=True, null=True)
    tax_officer_id = models.CharField(max_length=18, verbose_name="办税员身份证", help_text="企业办税员的身份证号码", db_comment="企业办税员的身份证号码", blank=True, null=True)
    tax_officer_tax_password = models.CharField(max_length=100, verbose_name="办税员电子税务局密码", help_text="办税员的电子税务局登录密码", db_comment="办税员的电子税务局登录密码", blank=True, null=True)
    tripartite_agreement_account = models.CharField(max_length=30, blank=True, verbose_name="三方协议账户", help_text="用于税费扣缴的三方协议账户", db_comment="用于税费扣缴的三方协议账户", null=True)
    tax_categories = models.TextField(verbose_name="税种", help_text="企业需要缴纳的税种", db_comment="企业需要缴纳的税种", blank=True, null=True)
    personal_income_tax_staff = models.TextField(verbose_name="申报个税人员", help_text="需要申报个人所得税的员工信息", db_comment="需要申报个人所得税的员工信息", blank=True, null=True)
    personal_income_tax_password = models.CharField(max_length=100, verbose_name="个税密码", help_text="个人所得税申报系统的登录密码", db_comment="个人所得税申报系统的登录密码", blank=True, null=True)
    legal_person_id_images = models.JSONField(default=list, verbose_name="法人身份证图片", help_text="法定代表人身份证的扫描件或照片地址，最多三张", db_comment="法定代表人身份证的扫描件或照片地址，最多三张")
    other_id_images = models.JSONField(default=list, verbose_name="其他身份证图片", help_text="其他相关人员身份证的扫描件或照片地址，最多三张", db_comment="其他相关人员身份证的扫描件或照片地址，最多三张")
    business_license_images = models.JSONField(default=list, verbose_name="营业执照图片", help_text="企业营业执照的扫描件或照片地址，最多三张", db_comment="企业营业执照的扫描件或照片地址，最多三张")
    bank_account_license_images = models.JSONField(default=list, verbose_name="开户许可图片", help_text="企业开户许可证的扫描件或照片地址，最多三张", db_comment="企业开户许可证的扫描件或照片地址，最多三张")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间", help_text="记录的最后更新时间", db_comment="记录的最后更新时间", blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间", help_text="记录的创建时间", db_comment="记录的创建时间", blank=True, null=True)
    submitter = models.CharField(max_length=100, verbose_name="提交人", help_text="创建或最后修改该记录的用户", db_comment="创建或最后修改该记录的用户", blank=True, null=True)
    business_status = models.CharField(max_length=20, choices=BUSINESS_STATUS_CHOICES, default='ongoing', verbose_name="业务状态", help_text="当前业务的状态", db_comment="当前业务的状态", blank=True, null=True)
    
    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = '客户信息'
        verbose_name_plural = '客户信息'