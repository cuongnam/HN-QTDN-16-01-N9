from odoo import models, fields, api

class ProjectManagementBudgets(models.Model):
    _name = 'budgets'
    _description = 'Project Management Budgets'

    budgets_id = fields.Char(string='Mã ngân sách', required=True)
    budgets_name = fields.Char(string='Tên khoản mục ngân sách', required=True)
    
    projects_id = fields.Many2one('projects', string='Thuộc Dự án', ondelete='cascade')
    
    budget_planned = fields.Float(string='Ngân sách dự kiến')
    budget_allocated = fields.Float(string='Ngân sách đã cấp phát')
    budget_reserved = fields.Float(string='Ngân sách dự phòng')
    
    expense_ids = fields.One2many('expenses', 'budgets_id', string='Chi tiết chi tiêu')
    
    budget_spent = fields.Float(string='Ngân sách đã tiêu', compute='_compute_budget_spent')
    budget_difference = fields.Float(string='Chênh lệch còn lại', compute='_compute_budget_diff')

    @api.depends('expense_ids.amount')
    def _compute_budget_spent(self):
        for rec in self:
            rec.budget_spent = sum(rec.expense_ids.mapped('amount'))

    @api.depends('budget_allocated', 'budget_spent')
    def _compute_budget_diff(self):
        for rec in self:
            rec.budget_difference = rec.budget_allocated - rec.budget_spent