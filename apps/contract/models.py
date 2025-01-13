from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Contract(models.Model):
    CONTRACT_STATUS_CHOICES = (
        ('未签署', '未签署'),
        ('生效中', '生效中'),
        ('已过期', '已过期'),
        ('已作废', '已作废')
    )
    
    BUSINESS_TYPE_CHOICES = (
        ('代理记账合同', '代理记账合同'),
        ('社保代理合同', '社保代理合同'),
    )
    
    # 基本信息
    contract_no = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='合同编号',
        help_text='合同编号',
        db_comment='合同编号'
    )
    
    business_type = models.CharField(
        max_length=20,
        choices=BUSINESS_TYPE_CHOICES,
        verbose_name='业务类型',
        help_text='业务类型：代理记账/社保代理',
        db_comment='业务类型'
    )
    
    # 客户信息（甲方）
    customer_name = models.CharField(
        max_length=255,
        verbose_name='客户名称',
        help_text='客户名称',
        db_comment='客户名称'
    )
    customer_code = models.CharField(
        max_length=50,
        verbose_name='客户统一社会信用代码',
        help_text='客户统一社会信用代码',
        db_comment='客户统一社会信用代码'
    )
    customer_address = models.CharField(
        max_length=255,
        verbose_name='客户地址',
        help_text='客户地址',
        db_comment='客户地址'
    )
    customer_phone = models.CharField(
        max_length=20,
        verbose_name='客户电话',
        help_text='客户电话',
        db_comment='客户电话'
    )
    customer_contact = models.CharField(
        max_length=50,
        verbose_name='客户联系人',
        help_text='客户联系人',
        db_comment='客户联系人'
    )
    
    # 公司信息（乙方）
    company_name = models.CharField(
        max_length=255,
        verbose_name='公司名称',
        help_text='公司名称',
        db_comment='公司名称'
    )
    company_code = models.CharField(
        max_length=50,
        verbose_name='公司统一社会信用代码',
        help_text='公司统一社会信用代码',
        db_comment='公司统一社会信用代码'
    )
    company_address = models.CharField(
        max_length=255,
        verbose_name='公司地址',
        help_text='公司地址',
        db_comment='公司地址'
    )
    company_phone = models.CharField(
        max_length=20,
        verbose_name='公司电话',
        help_text='公司电话',
        db_comment='公司电话'
    )
    business_person = models.CharField(
        max_length=50,
        verbose_name='业务人员',
        help_text='业务人员',
        db_comment='业务人员'
    )
    
    # 合同金额信息
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='合同金额',
        help_text='合同金额',
        db_comment='合同金额'
    )
    
    # 合同日期
    sign_date = models.DateField(
        verbose_name='签订日期',
        help_text='合同签订日期',
        db_comment='合同签订日期'
    )
    start_date = models.DateField(
        verbose_name='开始日期',
        help_text='合同开始日期',
        db_comment='合同开始日期'
    )
    expire_date = models.DateField(
        verbose_name='到期日期',
        help_text='合同到期日期',
        db_comment='合同到期日期'
    )
    
    # 合同状态
    status = models.CharField(
        max_length=20,
        choices=CONTRACT_STATUS_CHOICES,
        default='未签署',
        verbose_name='合同状态',
        help_text='合同状态：未签署/生效中/已过期/已作废',
        db_comment='合同状态'
    )
    
    # 其他信息
    remark = models.TextField(
        null=True,
        blank=True,
        verbose_name='备注',
        help_text='合同备注信息',
        db_comment='合同备注信息'
    )
    contract_files = models.JSONField(
        default=list,
        verbose_name='合同文件',
        help_text='合同文件URL列表',
        db_comment='合同文件URL列表'
    )
    
    # 审计字段
    submitter = models.CharField(
        max_length=50,
        verbose_name='提交人',
        help_text='提交人',
        db_comment='提交人'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间',
        help_text='创建时间',
        db_comment='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间',
        help_text='更新时间',
        db_comment='更新时间'
    )

    class Meta:
        db_table = 'zy_contract'
        verbose_name = '合同'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['contract_no']),
            models.Index(fields=['customer_name']),
            models.Index(fields=['status']),
            models.Index(fields=['business_type']),
        ]

    def __str__(self):
        return f"{self.contract_no}-{self.customer_name}"