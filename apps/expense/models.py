from django.db import models
from django.conf import settings
from django.core.validators import MaxLengthValidator
from django.utils import timezone

class Expense(models.Model):
    company_name = models.CharField(max_length=255, verbose_name='企业名称', db_comment='企业名称', null=True, blank=True)
    company_type = models.CharField(max_length=100, verbose_name='企业类型', db_comment='企业类型', null=True, blank=True)
    company_location = models.CharField(max_length=255, verbose_name='企业归属地', db_comment='企业归属地', null=True, blank=True)
    license_type = models.CharField(max_length=100, verbose_name='办照类型', db_comment='办照类型', null=True, blank=True)
    license_fee = models.IntegerField(verbose_name='办照费用', db_comment='办照费用', null=True, blank=True)
    one_time_address_fee = models.IntegerField(verbose_name='一次性地址费', db_comment='一次性地址费', null=True, blank=True)
    brand_fee = models.IntegerField(verbose_name='牌子费', db_comment='牌子费', null=True, blank=True)
    seal_fee = models.IntegerField(verbose_name='刻章费', db_comment='刻章费', null=True, blank=True)
    agency_type = models.CharField(max_length=100, verbose_name='代理类型', db_comment='代理类型', null=True, blank=True)
    agency_fee = models.IntegerField(verbose_name='代理费', db_comment='代理费', null=True, blank=True)
    accounting_software_fee = models.IntegerField(verbose_name='记账软件费', db_comment='记账软件费', null=True, blank=True)
    address_fee = models.IntegerField(verbose_name='地址费', db_comment='地址费', null=True, blank=True)
    agency_start_date = models.DateField(verbose_name='代理开始日期', db_comment='代理开始日期', null=True, blank=True)
    agency_end_date = models.DateField(verbose_name='代理结束日期', db_comment='代理结束日期', null=True, blank=True)
    business_type = models.CharField(max_length=100, verbose_name='业务类型', db_comment='业务类型', null=True, blank=True)
    contract_type = models.CharField(max_length=100, verbose_name='合同类型', db_comment='合同类型', null=True, blank=True)
    contract_image = models.CharField(max_length=255, null=True, blank=True, verbose_name='合同图片', db_comment='合同图片')
    invoice_software_provider = models.CharField(max_length=255, verbose_name='开票软件服务商', db_comment='开票软件服务商', null=True, blank=True)
    invoice_software_fee = models.IntegerField(verbose_name='开票软件费', db_comment='开票软件费', null=True, blank=True)
    invoice_software_start_date = models.DateField(verbose_name='开票软件开始日期', db_comment='开票软件开始日期', null=True, blank=True)
    invoice_software_end_date = models.DateField(verbose_name='开票软件结束日期', db_comment='开票软件结束日期', null=True, blank=True)
    insurance_types = models.CharField(max_length=255, verbose_name='参保险种', db_comment='参保险种', null=True, blank=True)
    insured_count = models.IntegerField(verbose_name='参保人数', db_comment='参保人数', null=True, blank=True)
    social_insurance_agency_fee = models.IntegerField(verbose_name='社保代理费', db_comment='社保代理费', null=True, blank=True)
    social_insurance_start_date = models.DateField(verbose_name='社保开始日期', db_comment='社保开始日期', null=True, blank=True)
    social_insurance_end_date = models.DateField(verbose_name='社保结束日期', db_comment='社保结束日期', null=True, blank=True)
    statistical_report_fee = models.IntegerField(verbose_name='统计局报表费', db_comment='统计局报表费', null=True, blank=True)
    statistical_start_date = models.DateField(verbose_name='统计开始日期', db_comment='统计开始日期', null=True, blank=True)
    statistical_end_date = models.DateField(verbose_name='统计结束日期', db_comment='统计结束日期', null=True, blank=True)
    change_business = models.CharField(max_length=255, verbose_name='变更业务', db_comment='变更业务', null=True, blank=True)
    change_fee = models.IntegerField(verbose_name='变更收费', db_comment='变更收费', null=True, blank=True)
    administrative_license = models.CharField(max_length=255, verbose_name='行政许可', db_comment='行政许可', null=True, blank=True)
    administrative_license_fee = models.IntegerField(verbose_name='行政许可收费', db_comment='行政许可收费', null=True, blank=True)
    other_business = models.CharField(max_length=255, verbose_name='其他业务', db_comment='其他业务', null=True, blank=True)
    other_business_fee = models.IntegerField(verbose_name='其他业务收费', db_comment='其他业务收费', null=True, blank=True)
    proof_of_charge = models.JSONField(
        default=list,
        blank=True,
        null=True,
        validators=[MaxLengthValidator(3)],
        verbose_name='收费凭证',
        help_text='收费凭证（最多3张）'
    )
    total_fee = models.IntegerField(verbose_name='总费用', db_comment='总费用', null=True, blank=True)
    submitter = models.CharField(max_length=100, verbose_name='提交人', db_comment='提交人', null=True, blank=True)
    create_time = models.DateTimeField(default=timezone.now, verbose_name='创建日期', db_comment='创建日期')
    charge_date = models.DateField(verbose_name='收费日期', db_comment='收费日期', null=True, blank=True)
    charge_method = models.CharField(max_length=100, verbose_name='收费方式', db_comment='收费方式', null=True, blank=True)
    auditor = models.CharField(max_length=100, verbose_name='审核员', db_comment='审核员', null=True, blank=True)
    audit_date = models.DateField(null=True, blank=True, verbose_name='审核日期', db_comment='审核日期')
    status = models.IntegerField(choices=((0, '未审核'), (1, '已审核'), (2, '已拒绝')), default=0, verbose_name='状态', db_comment='状态：0-未审核，1-已审核，2-已拒绝')
    reject_reason = models.TextField(blank=True, null=True, verbose_name='拒绝原因', db_comment='审核拒绝原因')
    remarks = models.TextField(blank=True, verbose_name='备注', db_comment='备注信息')

    def __str__(self):
        return self.company_name or ''

    class Meta:
        verbose_name = '费用记录'
        verbose_name_plural = '费用记录'
        db_table = 'zy_expense'
