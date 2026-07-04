# from odoo import models, fields, api

# class ProjectManagementProjects(models.Model):
#     _name = 'projects'
#     _description = 'Project Management Projects'

#     projects_id = fields.Char(string='Mã dự án', required=True)
#     projects_name = fields.Char(string='Tên dự án (EN)', required=True)
    
#     # Kết nối với nhan_vien của module nhan_su/quan_ly_cong_viec
#     manager_name = fields.Many2one('nhan_vien', string='Trưởng dự án') 
    
#     # KẾT NỐI MỚI: Liên kết 1-1 hoặc 1-N sang du_an của quan_ly_cong_viec
#     du_an_id = fields.Many2one('du_an', string='Dự án gốc (QLCV)')
    
#     start_date = fields.Date(string='Ngày bắt đầu')
#     actual_end_date = fields.Date(string='Ngày kết thúc thực tế')
#     status = fields.Selection([
#         ('draft', 'Mới'),
#         ('open', 'Đang chạy'),
#         ('close', 'Đóng'),
#     ], string='Trạng thái', default='draft')
#     ly_do_1 = fields.Text(string='Lý do / Ghi chú')
    
#     # Quan hệ One2many tới Tasks và Budgets nội bộ
#     task_ids = fields.One2many('taskss', 'projects_id', string='Danh sách Tasks')
#     budget_ids = fields.One2many('budgets', 'projects_id', string='Ngân sách dự án')

#     progress = fields.Float(string='Tiến độ (%)', compute='_compute_progress')

#     @api.depends('task_ids.progress')
#     def _compute_progress(self):
#         for rec in self:
#             # Logic tính toán tiến độ trung bình dựa trên các taskss
#             tasks = rec.task_ids
#             if tasks:
#                 rec.progress = sum(tasks.mapped('progress')) / len(tasks)
#             else:
#                 rec.progress = 0.0

# from odoo import models, fields, api
# from odoo.exceptions import ValidationError

# class ProjectManagementProjects(models.Model):
#     _name = 'projects'
#     _description = 'Project Management Projects'
#     _rec_name = 'projects_name'

#     projects_id = fields.Char(string='Mã dự án', required=True)
#     projects_name = fields.Char(string='Tên dự án (EN)', required=True)
#     manager_name = fields.Many2one('nhan_vien', string='Trưởng dự án') 
#     du_an_id = fields.Many2one('du_an', string='Dự án gốc (QLCV)', ondelete='set null')
    
#     start_date = fields.Date(string='Ngày bắt đầu')
#     actual_end_date = fields.Date(string='Ngày kết thúc thực tế')
    
#     # 1. Bổ sung trạng thái 'cancelled' vào Selection
#     status = fields.Selection([
#         ('draft', 'Mới'),
#         ('open', 'Đang chạy'),
#         ('close', 'Đóng'),
#         ('cancelled', 'Đã hủy bỏ'), 
#     ], string='Trạng thái', default='draft')
    
#     ly_do_1 = fields.Text(string='Lý do / Ghi chú')
#     task_ids = fields.One2many('taskss', 'projects_id', string='Danh sách Tasks')
#     budget_ids = fields.One2many('budgets', 'projects_id', string='Ngân sách dự án')
#     progress = fields.Float(string='Tiến độ (%)', compute='_compute_progress')

#     @api.depends('task_ids.progress')
#     def _compute_progress(self):
#         for rec in self:
#             tasks = rec.task_ids
#             if tasks:
#                 rec.progress = sum(tasks.mapped('progress')) / len(tasks)
#             else:
#                 rec.progress = 0.0

#     @api.model
#     def create(self, vals):
#         if not vals.get('du_an_id') and vals.get('projects_name'):
#             du_an_val = {
#                 'ten_du_an': vals.get('projects_name'),
#                 'mo_ta': vals.get('ly_do_1') or '',
#                 'tien_do_du_an': 'chua_bat_dau',
#                 'nguoi_phu_trach_id': vals.get('manager_name') or False, 
#             }
#             new_du_an = self.env['du_an'].create(du_an_val)
#             vals['du_an_id'] = new_du_an.id
#         return super(ProjectManagementProjects, self).create(vals)

#     # 2. Xử lý nghiệp vụ khi sửa/hủy dự án
#     def write(self, vals):
#         res = super(ProjectManagementProjects, self).write(vals)
        
#         for rec in self:
#             # Nếu trạng thái chuyển sang HỦY BỎ
#             if vals.get('status') == 'cancelled':
#                 # Nghiệp vụ A: Đồng bộ trạng thái sang dự án gốc (nếu bảng du_an của bạn có trạng thái tương tự)
#                 if rec.du_an_id:
#                     # Giả sử bảng du_an cũ của bạn có trường tien_do_du_an dạng selection
#                     # Bạn có thể gán nó về trạng thái kết thúc/hủy tùy theo thiết kế bảng du_an cũ
#                     rec.du_an_id.write({'mo_ta': (rec.du_an_id.mo_ta or '') + '\n[Dự án đã bị hủy bỏ]'})
                
#                 # Nghiệp vụ B: Tự động chuyển toàn bộ Task chưa xong thuộc dự án này thành Hủy
#                 tasks_to_cancel = rec.task_ids.filtered(lambda t: t.status in ['todo', 'doing'])
#                 if tasks_to_cancel:
#                     # Cập nhật trạng thái taskss bên này (Lưu ý: bảng taskss cần có selection trạng thái hủy, ví dụ 'cancelled')
#                     tasks_to_cancel.write({'status': 'done', 'ly_do': 'Hủy theo dự án'}) 

#             # Đồng bộ thay đổi tên và người phụ trách thông thường
#             if rec.du_an_id:
#                 up_vals = {}
#                 if 'projects_name' in vals:
#                     up_vals['ten_du_an'] = vals['projects_name']
#                 if 'manager_name' in vals:
#                     up_vals['nguoi_phu_trach_id'] = vals['manager_name'] or False
#                 if up_vals:
#                     rec.du_an_id.write(up_vals)
#         return res
    
#     def action_open(self):
#         """ Kích hoạt trạng thái Đang chạy """
#         self.write({'status': 'open'})

#     def action_close(self):
#         """ Kích hoạt trạng thái Hoàn thành và đóng dự án """
#         self.write({'status': 'close'})

#     def action_cancel(self):
#         """ Kích hoạt trạng thái Hủy bỏ dự án """
#         self.write({'status': 'cancelled'})


# from odoo import models, fields, api
# from odoo.exceptions import ValidationError

# class ProjectManagementProjects(models.Model):
#     _name = 'projects'
#     _description = 'Project Management Projects'
#     _rec_name = 'projects_name'

#     projects_id = fields.Char(string='Mã dự án', required=True)
#     projects_name = fields.Char(string='Tên dự án (EN)', required=True)
#     manager_name = fields.Many2one('nhan_vien', string='Trưởng dự án') 
#     du_an_id = fields.Many2one('du_an', string='Dự án gốc (QLCV)', ondelete='set null')
    
#     start_date = fields.Date(string='Ngày bắt đầu')
#     actual_end_date = fields.Date(string='Ngày kết thúc thực tế')
    
#     status = fields.Selection([
#         ('draft', 'Mới'),
#         ('open', 'Đang chạy'),
#         ('close', 'Đóng'),
#         ('cancelled', 'Đã hủy bỏ'), 
#     ], string='Trạng thái', default='draft')
    
#     ly_do_1 = fields.Text(string='Lý do / Ghi chú')
#     task_ids = fields.One2many('taskss', 'projects_id', string='Danh sách Tasks')
#     budget_ids = fields.One2many('budgets', 'projects_id', string='Ngân sách dự án')
#     progress = fields.Float(string='Tiến độ (%)', compute='_compute_progress')

#     @api.depends('task_ids.progress')
#     def _compute_progress(self):
#         for rec in self:
#             tasks = rec.task_ids
#             if tasks:
#                 rec.progress = sum(tasks.mapped('progress')) / len(tasks)
#             else:
#                 rec.progress = 0.0

#     @api.model
#     def create(self, vals):
#         if not vals.get('du_an_id') and vals.get('projects_name'):
#             # Ánh xạ trạng thái khi tạo mới ban đầu
#             status_mapping = {
#                 'draft': 'chua_bat_dau',
#                 'open': 'dang_thuc_hien',
#                 'close': 'hoan_thanh',
#                 'cancelled': 'huy_bo'
#             }
#             current_status = vals.get('status', 'draft')
            
#             du_an_val = {
#                 'ten_du_an': vals.get('projects_name'),
#                 'mo_ta': vals.get('ly_do_1') or '',
#                 'tien_do_du_an': status_mapping.get(current_status, 'chua_bat_dau'),
#                 'nguoi_phu_trach_id': vals.get('manager_name') or False, 
#             }
#             new_du_an = self.env['du_an'].create(du_an_val)
#             vals['du_an_id'] = new_du_an.id
#         return super(ProjectManagementProjects, self).create(vals)

#     def write(self, vals):
#         # 1. Gọi hàm write gốc để cập nhật dữ liệu của bảng projects trước
#         res = super(ProjectManagementProjects, self).write(vals)
        
#         # 2. Thực hiện đồng bộ dây chuyền sang bảng du_an gốc
#         status_mapping = {
#             'draft': 'chua_bat_dau',
#             'open': 'dang_thuc_hien',
#             'close': 'hoan_thanh',
#             'cancelled': 'huy_bo'
#         }

#         for rec in self:
#             if rec.du_an_id:
#                 up_vals = {}
#                 # Đồng bộ tên dự án
#                 if 'projects_name' in vals:
#                     up_vals['ten_du_an'] = vals['projects_name']
                
#                 # Đồng bộ người phụ trách (Trưởng dự án)
#                 if 'manager_name' in vals:
#                     up_vals['nguoi_phu_trach_id'] = vals['manager_name'] or False
                
#                 # Đồng bộ trạng thái/tiến độ khi bấm các nút điều hướng trên header
#                 if 'status' in vals:
#                     up_vals['tien_do_du_an'] = status_mapping.get(vals['status'], 'chua_bat_dau')
                    
#                     # Nghiệp vụ bổ sung nếu dự án bị hủy
#                     if vals['status'] == 'cancelled':
#                         up_vals['mo_ta'] = (rec.du_an_id.mo_ta or '') + '\n[Dự án đã bị hủy bỏ]'
#                         tasks_to_cancel = rec.task_ids.filtered(lambda t: t.status in ['todo', 'doing'])
#                         if tasks_to_cancel:
#                             tasks_to_cancel.write({'status': 'done', 'ly_do': 'Hủy theo dự án'})

#                 # Thực hiện cập nhật sang bảng du_an
#                 if up_vals:
#                     rec.du_an_id.write(up_vals)
#         return res
    
#     def action_open(self):
#         self.write({'status': 'open'})

#     def action_close(self):
#         self.write({'status': 'close'})

#     def action_cancel(self):
#         self.write({'status': 'cancelled'})


from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ProjectManagementProjects(models.Model):
    _name = 'projects'
    _description = 'Project Management Projects'
    _rec_name = 'projects_name'

    projects_id = fields.Char(string='Mã dự án', required=True)    
    # THÊM DÒNG NÀY ĐỂ CHẶN TRÙNG MÃ DỰ ÁN DƯỚI DATABASE
    _sql_constraints = [
        ('projects_id_unique', 'unique(projects_id)', 'Mã dự án này đã tồn tại trong hệ thống! Vui lòng nhập mã khác.')
    ]
    projects_name = fields.Char(string='Tên dự án (EN)', required=True)
    manager_name = fields.Many2one('nhan_vien', string='Trưởng dự án') 
    du_an_id = fields.Many2one('du_an', string='Dự án gốc (QLCV)', ondelete='set null')
    
    start_date = fields.Date(string='Ngày bắt đầu')
    actual_end_date = fields.Date(string='Ngày kết thúc thực tế')
    
    status = fields.Selection([
        ('draft', 'Mới'),
        ('open', 'Đang chạy'),
        ('close', 'Đóng'),
        ('cancelled', 'Đã hủy bỏ'), 
    ], string='Trạng thái', default='draft')
    
    ly_do_1 = fields.Text(string='Lý do / Ghi chú')
    task_ids = fields.One2many('taskss', 'projects_id', string='Danh sách Tasks')
    budget_ids = fields.One2many('budgets', 'projects_id', string='Ngân sách dự án')
    progress = fields.Float(string='Tiến độ (%)', compute='_compute_progress')

    @api.depends('task_ids.progress')
    def _compute_progress(self):
        for rec in self:
            tasks = rec.task_ids
            if tasks:
                rec.progress = sum(tasks.mapped('progress')) / len(tasks)
            else:
                rec.progress = 0.0

    @api.constrains('projects_id')
    def _check_unique_projects_id(self):
        """ Bắn lỗi cảnh báo nếu phát hiện mã dự án bị trùng lặp trên giao diện """
        for rec in self:
            if rec.projects_id:
                # Tìm kiếm xem có bản ghi nào khác có cùng projects_id nhưng khác ID bản ghi hiện tại không
                duplicate = self.search([('projects_id', '=', rec.projects_id), ('id', '!=', rec.id)], limit=1)
                if duplicate:
                    raise ValidationError(f"Mã dự án '{rec.projects_id}' đã được sử dụng cho dự án '{duplicate.projects_name}'. Vui lòng chọn mã khác!")            

    @api.constrains('start_date', 'actual_end_date')
    def _check_dates(self):
        """ Ràng buộc: Ngày kết thúc thực tế phải lớn hơn hoặc bằng Ngày bắt đầu """
        for rec in self:
            if rec.start_date and rec.actual_end_date:
                if rec.actual_end_date < rec.start_date:
                    raise ValidationError(
                        f"Dự án '{rec.projects_name}' có ngày kết thúc thực tế ({rec.actual_end_date}) "
                        f"nhỏ hơn ngày bắt đầu ({rec.start_date})! Vui lòng kiểm tra lại."
                    )
                
    @api.model
    def create(self, vals):
        if not vals.get('du_an_id') and vals.get('projects_name'):
            status_mapping = {
                'draft': 'chua_bat_dau',
                'open': 'dang_thuc_hien',
                'close': 'hoan_thanh',
                'cancelled': 'huy_bo'
            }
            current_status = vals.get('status', 'draft')
            
            # Bóc tách chính xác ID người quản lý để truyền sang làm người phụ trách
            manager_id = vals.get('manager_name')
            if isinstance(manager_id, models.BaseModel):
                manager_id = manager_id.id

            du_an_val = {
                'ten_du_an': vals.get('projects_name'),
                'mo_ta': vals.get('ly_do_1') or '',
                'tien_do_du_an': status_mapping.get(current_status, 'chua_bat_dau'),
                'nguoi_phu_trach_id': manager_id or False, 
            }
            new_du_an = self.env['du_an'].create(du_an_val)
            vals['du_an_id'] = new_du_an.id
        return super(ProjectManagementProjects, self).create(vals)

    def write(self, vals):
        res = super(ProjectManagementProjects, self).write(vals)
        status_mapping = {
            'draft': 'chua_bat_dau',
            'open': 'dang_thuc_hien',
            'close': 'hoan_thanh',
            'cancelled': 'huy_bo'
        }

        for rec in self:
            if rec.du_an_id:
                up_vals = {}
                if 'projects_name' in vals:
                    up_vals['ten_du_an'] = vals['projects_name']
                
                if 'manager_name' in vals:
                    manager_id = vals['manager_name']
                    if isinstance(manager_id, models.BaseModel):
                        manager_id = manager_id.id
                    up_vals['nguoi_phu_trach_id'] = manager_id or False
                
                if 'status' in vals:
                    up_vals['tien_do_du_an'] = status_mapping.get(vals['status'], 'chua_bat_dau')
                    if vals['status'] == 'cancelled':
                        up_vals['mo_ta'] = (rec.du_an_id.mo_ta or '') + '\n[Dự án đã bị hủy bỏ]'
                        tasks_to_cancel = rec.task_ids.filtered(lambda t: t.status in ['todo', 'doing'])
                        if tasks_to_cancel:
                            tasks_to_cancel.write({'status': 'done', 'ly_do': 'Hủy theo dự án'})

                if up_vals:
                    rec.du_an_id.write(up_vals)
        return res
    
    def action_open(self):
        self.write({'status': 'open'})

    def action_close(self):
        self.write({'status': 'close'})

    def action_cancel(self):
        self.write({'status': 'cancelled'})