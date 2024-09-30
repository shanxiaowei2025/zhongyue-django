from django.db import models
from django.conf import settings

class Expense(models.Model):
    company_name = models.CharField(max_length=255, verbose_name='企业名称', db_comment='企业名称')
    company_type = models.CharField(max_length=100, verbose_name='企业类型', db_comment='企业类型')
    company_location = models.CharField(max_length=255, verbose_name='企业归属地', db_comment='企业归属地')
    license_type = models.CharField(max_length=100, verbose_name='办照类型', db_comment='办照类型')
    license_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='办照费用', db_comment='办照费用')
    one_time_address_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='一次性地址费', db_comment='一次性地址费')
    brand_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='牌子费', db_comment='牌子费')
    seal_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='刻章费', db_comment='刻章费')
    agency_type = models.CharField(max_length=100, verbose_name='代理类型', db_comment='代理类型')
    agency_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='代理费', db_comment='代理费')
    accounting_software_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='记账软件费', db_comment='记账软件费')
    address_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='地址费', db_comment='地址费')
    agency_start_date = models.DateField(verbose_name='代理开始日期', db_comment='代理开始日期')
    agency_end_date = models.DateField(verbose_name='代理结束日期', db_comment='代理结束日期')
    business_type = models.CharField(max_length=100, verbose_name='业务类型', db_comment='业务类型')
    contract_type = models.CharField(max_length=100, verbose_name='合同类型', db_comment='合同类型')
    contract_image = models.ImageField(upload_to='contract_images/', null=True, blank=True, verbose_name='合同图片', db_comment='合同图片')
    invoice_software_provider = models.CharField(max_length=255, verbose_name='开票软件服务商', db_comment='开票软件服务商')
    invoice_software_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='开票软件费', db_comment='开票软件费')
    invoice_software_start_date = models.DateField(verbose_name='开票软件开始日期', db_comment='开票软件开始日期')
    invoice_software_end_date = models.DateField(verbose_name='开票软件结束日期', db_comment='开票软件结束日期')
    insurance_types = models.CharField(max_length=255, verbose_name='参保险种', db_comment='参保险种')
    insured_count = models.IntegerField(verbose_name='参保人数', db_comment='参保人数')
    social_insurance_agency_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='社保代理费', db_comment='社保代理费')
    social_insurance_start_date = models.DateField(verbose_name='社保开始日期', db_comment='社保开始日期')
    social_insurance_end_date = models.DateField(verbose_name='社保结束日期', db_comment='社保结束日期')
    statistical_report_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='统计局报表费', db_comment='统计局报表费')
    statistical_start_date = models.DateField(verbose_name='统计开始日期', db_comment='统计开始日期')
    statistical_end_date = models.DateField(verbose_name='统计结束日期', db_comment='统计结束日期')
    change_business = models.CharField(max_length=255, verbose_name='变更业务', db_comment='变更业务')
    change_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='变更收费', db_comment='变更收费')
    administrative_license = models.CharField(max_length=255, verbose_name='行政许可', db_comment='行政许可')
    administrative_license_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='行政许可收费', db_comment='行政许可收费')
    other_business = models.CharField(max_length=255, verbose_name='其他业务', db_comment='其他业务')
    other_business_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='其他业务收费', db_comment='其他业务收费')
    proof_of_charge = models.ImageField(upload_to='proof_of_charge/', null=True, blank=True, verbose_name='收费凭证', db_comment='收费凭证')
    total_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='总费用', db_comment='总费用')
    submitter = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='提交人ID',
        db_comment='提交人ID'
    )
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建日期', db_comment='创建日期')
    charge_date = models.DateField(verbose_name='收费日期', db_comment='收费日期')
    charge_method = models.CharField(max_length=100, verbose_name='收费方式', db_comment='收费方式')
    auditor = models.CharField(max_length=100, verbose_name='审核员', db_comment='审核员')
    audit_date = models.DateField(null=True, blank=True, verbose_name='审核日期', db_comment='审核日期')
    status = models.IntegerField(choices=((0, '未审核'), (1, '已审核')), default=0, verbose_name='状态', db_comment='状态：0-未审核，1-已审核')
    remarks = models.TextField(blank=True, verbose_name='备注', db_comment='备注信息')

    def __str__(self):
        return self.company_name

    class Meta:
        verbose_name = '费用记录'
        verbose_name_plural = '费用记录'