# from odoo import models, fields, api

# class ProjectManagementTasks(models.Model):
#     _name = 'taskss'
#     _description = 'Project Management Tasks'

#     taskss_id = fields.Char(string='Mã Công Việc', required=True)
#     taskss_name = fields.Char(string='Tên Công Việc (EN)', required=True)
    
#     # Quan hệ Many2one tới dự án của module này
#     projects_id = fields.Many2one('projects', string='Thuộc Dự án', ondelete='cascade')
    
#     # KẾT NỐI MỚI: Liên kết sang công việc của module quan_ly_cong_viec
#     cong_viec_id = fields.Many2one('cong_viec', string='Công việc liên kết (QLCV)')

#     start_date = fields.Date(string='Ngày bắt đầu')
#     deadline = fields.Datetime(string='Hạn chót')
#     priority = fields.Selection([('0', 'Thấp'), ('1', 'Thường'), ('2', 'Cao')], string='Độ ưu tiên')
#     status = fields.Selection([('todo', 'Cần làm'), ('doing', 'Đang làm'), ('done', 'Xong')], string='Trạng thái')
#     ly_do = fields.Text(string='Ghi chú/Lý do chậm trễ')
#     progress = fields.Float(string='Tiến độ task (%)')
    
#     expense_ids = fields.One2many('expenses', 'taskss_id', string='Chi phí phát sinh')
from odoo import models, fields, api

class ProjectManagementTasks(models.Model):
    _name = 'taskss'
    _description = 'Project Management Tasks'
    _rec_name = 'taskss_name'

    taskss_id = fields.Char(string='Mã Công Việc', required=True)
    taskss_name = fields.Char(string='Tên Công Việc (EN)', required=True)
    
    projects_id = fields.Many2one('projects', string='Thuộc Dự án', ondelete='cascade')
    cong_viec_id = fields.Many2one('cong_viec', string='Công việc liên kết (QLCV)', ondelete='set null')

    start_date = fields.Date(string='Ngày bắt đầu')
    deadline = fields.Datetime(string='Hạn chót')
    priority = fields.Selection([('0', 'Thấp'), ('1', 'Thường'), ('2', 'Cao')], string='Độ ưu tiên')
    status = fields.Selection([('todo', 'Cần làm'), ('doing', 'Đang làm'), ('done', 'Xong')], string='Trạng thái')
    ly_do = fields.Text(string='Ghi chú/Lý do chậm trễ')
    progress = fields.Float(string='Tiến độ task (%)')
    
    expense_ids = fields.One2many('expenses', 'taskss_id', string='Chi phí phát sinh')

    # 🛠️ TỰ ĐỘNG ĐỒNG BỘ TASK
    @api.model
    def create(self, vals):
        if not vals.get('cong_viec_id') and vals.get('taskss_name'):
            project = self.env['projects'].browse(vals.get('projects_id'))
            if project and project.du_an_id:
                cong_viec_val = {
                    'ten_cong_viec': vals.get('taskss_name'),
                    'du_an_id': project.du_an_id.id, # Gắn task vào đúng dự án gốc vừa tự động tạo
                    'han_chot': vals.get('deadline'),
                    'mo_ta': vals.get('ly_do') or '',
                }
                new_cong_viec = self.env['cong_viec'].create(cong_viec_val)
                vals['cong_viec_id'] = new_cong_viec.id

        return super(ProjectManagementTasks, self).create(vals)
    # Thêm đoạn này vào model chứa chi phí phát sinh hoặc model taskss để chặn ghi nhận chi phí
    @api.constrains('expense_ids')
    def _check_project_cancelled(self):
        for rec in self:
            if rec.projects_id and rec.projects_id.status == 'cancelled':
                raise ValidationError("Không thể thêm hoặc chỉnh sửa chi phí phát sinh cho một dự án đã bị hủy bỏ!")