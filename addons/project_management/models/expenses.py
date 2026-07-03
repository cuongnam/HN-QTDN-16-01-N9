from odoo import models, fields

class ProjectManagementExpenses(models.Model):
    _name = 'expenses'
    _description = 'Project Management Expenses'

    expenses_name = fields.Char(string='Lý do chi tiêu', required=True)
    amount = fields.Float(string='Số tiền chi', required=True)
    date = fields.Date(string='Ngày chi', default=fields.Date.context_today)
    
    # Liên kết song song tới cả Task và danh mục Ngân sách của Dự án
    taskss_id = fields.Many2one('taskss', string='Chi cho Task', ondelete='set null')
    budgets_id = fields.Many2one('budgets', 'Thuộc dòng ngân sách', ondelete='cascade')