# Part of Hibou Suite Professional. See LICENSE_PROFESSIONAL file for full copyright and licensing details.

from .general import _state_applies, sit_wage, _general_rate


def co_colorado_state_income_withholding(payslip, categories, worked_days, inputs):
    """
    Returns SIT eligible wage and rate.

    :return: result, result_rate (wage, percent)
    """
    state_code = 'CO'
    if not _state_applies(payslip, state_code):
        return 0.0, 0.0

    # Determine Wage
    wage = sit_wage(payslip, categories)
    if not wage:
        return 0.0, 0.0

    filing_status = payslip.contract_id.us_payroll_config_value('fed_941_fit_w4_filing_status')
    if not filing_status:
        return 0.0, 0.0

    state_exempt = payslip.contract_id.us_payroll_config_value('state_income_tax_exempt')
    if state_exempt:
        return 0.0, 0.0

    pay_periods = payslip.dict.get_pay_periods_in_year()
    additional = payslip.contract_id.us_payroll_config_value('state_income_tax_additional_withholding')
    exemption_rate = payslip.rule_parameter('us_co_sit_exemption_rate')
    tax_rate = payslip.rule_parameter('us_co_sit_tax_rate')

    taxable_income = wage * pay_periods
    if filing_status == 'married':
        taxable_income -= exemption_rate * 2
    else:
        taxable_income -= exemption_rate

    withholding = taxable_income * (tax_rate / 100)

    withholding = max(withholding, 0.0)
    withholding = withholding / pay_periods
    withholding += additional
    return wage, -((withholding / wage) * 100.0)

def _co_colorado_fmli(payslip, categories, worked_days, inputs, inner_rate=None):
    if not inner_rate:
        return 0.0, 0.0

    if not _state_applies(payslip, 'CO'):
        return 0.0, 0.0

    wage = categories.GROSS
    year = payslip.dict.get_year()
    rate = payslip.rule_parameter(inner_rate)
    return _general_rate(payslip, wage, 0.0, rate=rate)


def co_colorado_fmli_er(payslip, categories, worked_days, inputs):
    return _co_colorado_fmli(payslip, categories, worked_days, inputs, inner_rate='us_co_famli_rate_er')


def co_colorado_fmli_ee(payslip, categories, worked_days, inputs):
    return _co_colorado_fmli(payslip, categories, worked_days, inputs, inner_rate='us_co_famli_rate_ee')
