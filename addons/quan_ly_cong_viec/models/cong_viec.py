from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

class CongViec(models.Model):
    _name = 'cong_viec'
    _description = 'Công Việc Dự Án'
    _rec_name = 'ten_cong_viec'

    ten_cong_viec = fields.Char(string='Tên Công Việc' )
    mo_ta = fields.Text(string='Mô Tả')
    # du_an_id = fields.Many2one('du_an', string='Dự Án', required=True, ondelete='cascade')
    # SỬA DÒNG NÀY: Thêm domain lọc trạng thái dự án
    du_an_id = fields.Many2one(
        'du_an', 
        string='Dự Án', 
        required=True, 
        ondelete='cascade',
        domain="[('tien_do_du_an', 'not in', ['huy_bo', 'hoan_thanh'])]"
    )
    nhom_id = fields.Many2one(
        'nhom_du_an',
        string='Nhóm thực hiện'
    )

    _sql_constraints = [
    (
        'unique_task_per_project',
        'unique(du_an_id, ten_cong_viec)',
        'Tên công việc đã tồn tại trong dự án.'
    )
]

    nhan_vien_ids = fields.Many2many('nhan_vien', 'cong_viec_nhan_vien_rel', 'cong_viec_id', 'nhan_vien_id', string='Nhân Viên Tham Gia')

    han_chot = fields.Datetime(string='Hạn Chót')
    giai_doan_id = fields.Many2one('giai_doan_cong_viec', string='Giai Đoạn')

    nhat_ky_cong_viec_ids = fields.One2many('nhat_ky_cong_viec', 'cong_viec_id', string='Nhật Ký Công Việc')

    thoi_gian_con_lai = fields.Char(string="Thời Gian Còn Lại", compute="_compute_thoi_gian_con_lai", store=True)
    
    danh_gia_nhan_vien_ids = fields.One2many('danh_gia_nhan_vien', 'cong_viec_id', string='Đánh Giá Nhân Viên')
    
    nhan_vien_display = fields.Char(string="Nhân Viên Tham Gia (Tên + Mã Định Danh)", compute="_compute_nhan_vien_display")

    phan_tram_cong_viec = fields.Float(
        string="Phần Trăm Hoàn Thành", 
        compute="_compute_phan_tram_cong_viec", 
        store=True
    )

    @api.depends('nhat_ky_cong_viec_ids.muc_do')
    def _compute_phan_tram_cong_viec(self):
        for record in self:
            if record.nhat_ky_cong_viec_ids:
                total_progress = sum(record.nhat_ky_cong_viec_ids.mapped('muc_do'))
                record.phan_tram_cong_viec = total_progress / len(record.nhat_ky_cong_viec_ids)
            else:
                record.phan_tram_cong_viec = 0.0

    
    @api.depends('nhan_vien_ids')
    def _compute_nhan_vien_display(self):
        for record in self:
            record.nhan_vien_display = ', '.join(record.nhan_vien_ids.mapped('display_name'))

    @api.depends('han_chot')
    def _compute_thoi_gian_con_lai(self):
        for record in self:
            if record.han_chot:
                now = datetime.now()
                delta = record.han_chot - now
                if delta.total_seconds() > 0:
                    days = delta.days
                    hours = delta.seconds // 3600
                    record.thoi_gian_con_lai = f"{days} ngày, {hours} giờ"
                else:
                    record.thoi_gian_con_lai = "Hết hạn"
            else:
                record.thoi_gian_con_lai = "Chưa có hạn chót"

    
    # @api.onchange('du_an_id')
    # def _onchange_du_an_id(self):
    #     if self.du_an_id:
    #         self.nhan_vien_ids = [(6, 0, self.du_an_id.nhan_vien_ids.ids)]
    @api.onchange('du_an_id')
    def _onchange_du_an_id(self):
        self.nhom_id = False
        self.nhan_vien_ids = [(6, 0, [])]

        if self.du_an_id:
            return {
                'domain': {
                    'nhom_id': [
                        ('id', 'in', self.du_an_id.nhom_ids.ids)
                    ]
                }
            }
    # @api.onchange('nhom_id')
    # def _onchange_nhom_id(self):
    #     if self.nhom_id:
    #         self.nhan_vien_ids = [
    #             (6, 0, self.nhom_id.nhan_vien_ids.ids)
    #         ]
    #     else:
    #         self.nhan_vien_ids = [(6, 0, [])]
    @api.onchange('nhom_id')
    def _onchange_nhom_id(self):
        # Xóa danh sách nhân viên cũ
        self.nhan_vien_ids = [(5, 0, 0)]

        if self.nhom_id:
            return {
                'domain': {
                    'nhan_vien_ids': [
                        ('id', 'in', self.nhom_id.nhan_vien_ids.ids)
                    ]
                }
            }
            
    @api.constrains('du_an_id')
    def _check_du_an_tien_do(self):
        for record in self:
            if record.du_an_id and record.du_an_id.tien_do_du_an == 'hoan_thanh':
                raise ValidationError("Không thể thêm công việc vào dự án đã hoàn thành.")
    
    # @api.constrains('nhan_vien_ids')
    # def _check_nhan_vien_trong_du_an(self):
    #     for record in self:
    #         if record.du_an_id:
    #             nhan_vien_du_an_ids = record.du_an_id.nhan_vien_ids.ids
    #             for nhan_vien in record.nhan_vien_ids:
    #                 if nhan_vien.id not in nhan_vien_du_an_ids:
    #                     raise ValidationError(f"Nhân viên {nhan_vien.display_name} không thuộc dự án này.")

    @api.constrains('du_an_id')
    def _check_du_an_tien_do(self):
        for record in self:
            if record.du_an_id and record.du_an_id.tien_do_du_an in ['hoan_thanh', 'huy_bo']:
                raise ValidationError("Không thể thêm hoặc gắn công việc vào dự án đã hoàn thành hoặc đã hủy bỏ.")
    @api.constrains('nhom_id', 'nhan_vien_ids')
    def _check_nhan_vien_trong_nhom(self):
        for record in self:
            if not record.nhom_id:
                continue

            nhom_members = record.nhom_id.nhan_vien_ids.ids

            for nv in record.nhan_vien_ids:
                if nv.id not in nhom_members:
                    raise ValidationError(
                        f"Nhân viên {nv.display_name} không thuộc nhóm {record.nhom_id.ten_nhom}."
                    )
    from odoo.exceptions import ValidationError

    @api.constrains('ten_cong_viec', 'du_an_id')
    def _check_duplicate_task_name(self):
        for rec in self:
            if not rec.ten_cong_viec or not rec.du_an_id:
                continue

            duplicate = self.search([
                ('id', '!=', rec.id),
                ('du_an_id', '=', rec.du_an_id.id),
                ('ten_cong_viec', '=', rec.ten_cong_viec),
            ], limit=1)

            if duplicate:
                raise ValidationError(
                    f"Công việc '{rec.ten_cong_viec}' đã tồn tại trong dự án này."
                )        
    # @api.model
    # def create(self, vals):
    #     """ LUỒNG NGƯỢC: Tạo từ quan_ly_cong_viec -> tự động sinh bên project_management """
    #     record = super(CongViec, self).create(vals)
        
    #     # Nếu đang trong luồng đồng bộ xuôi từ PM sang hoặc không có dự án thì bỏ qua
    #     if self.env.context.get('skip_sync') or not record.du_an_id:
    #         return record

    #     # Tìm dự án liên kết bên module project_management
    #     pm_project = self.env['projects'].search([('du_an_id', '=', record.du_an_id.id)], limit=1)
    #     if pm_project:
    #         # Tạo mã tự động cho Taskss dựa trên ID
    #         task_id_code = f"TASK{record.id:04d}"
            
    #         self.env['taskss'].with_context(skip_sync=True).create({
    #             'taskss_id': task_id_code,
    #             'taskss_name': record.ten_cong_viec or 'Công việc mới',
    #             'projects_id': pm_project.id,
    #             'cong_viec_id': record.id,
    #             'deadline': record.han_chot or False,
    #             'ly_do': record.mo_ta or '',
    #         })
    #     return record

    @api.model
    def create(self, vals):
        record = super(CongViec, self).create(vals)

        if self.env.context.get('skip_sync'):
            return record

        record._initialize_task()

        return record
    def _initialize_task(self):
        self.ensure_one()

        self._assign_default_stage()

        self._sync_to_project_management()
    def _assign_default_stage(self):
        self.ensure_one()

        if self.giai_doan_id or not self.du_an_id:
            return

        stage = self.env['giai_doan_cong_viec'].search(
            [('du_an_id', '=', self.du_an_id.id)],
            order='thu_tu asc',
            limit=1
        )

        if stage:
            self.giai_doan_id = stage.id
    # def _assign_default_members(self):
    #     self.ensure_one()

    #     if self.nhan_vien_ids:
    #         return

    #     if self.du_an_id.nhan_vien_ids:
    #         self.nhan_vien_ids = [
    #             (6, 0, self.du_an_id.nhan_vien_ids.ids)
    #         ]
    def _sync_to_project_management(self):
        self.ensure_one()

        if not self.du_an_id:
            return

        pm_project = self.env['projects'].search(
            [('du_an_id', '=', self.du_an_id.id)],
            limit=1
        )

        if not pm_project:
            return

        task_code = f"TASK{self.id:04d}"

        # self.env['taskss'].with_context(skip_sync=True).create({
        #     'taskss_id': task_code,
        #     'taskss_name': self.ten_cong_viec or 'Công việc mới',
        #     'projects_id': pm_project.id,
        #     'cong_viec_id': self.id,
        #     'deadline': self.han_chot,
        #     'ly_do': self.mo_ta or '',
        # })
        self.env['taskss'].with_context(skip_sync=True).create({
            'taskss_id': task_code,
            'taskss_name': self.ten_cong_viec or 'Công việc mới',
            'projects_id': pm_project.id,
            'cong_viec_id': self.id,
            'deadline': self.han_chot,
            'ly_do': self.mo_ta or '',
            'progress': self.phan_tram_cong_viec,
            'status': 'todo',
        })


    def write(self, vals):
        """ Đồng bộ cập nhật ngược từ quan_ly_cong_viec về lại project_management """
        res = super(CongViec, self).write(vals)
        if self.env.context.get('skip_sync'):
            return res

        for record in self:
            # Tìm taskss liên kết
            pm_task = self.env['taskss'].search([('cong_viec_id', '=', record.id)], limit=1)
            # if pm_task:
            #     up_vals = {}
            #     if 'ten_cong_viec' in vals:
            #         up_vals['taskss_name'] = vals['ten_cong_viec']
            #     if 'han_chot' in vals:
            #         up_vals['deadline'] = vals['han_chot']
            #     if 'mo_ta' in vals:
            #         up_vals['ly_do'] = vals['mo_ta']
            #     if up_vals:
            #         pm_task.with_context(skip_sync=True).write(up_vals)
            if pm_task:
                up_vals = {}

                if 'ten_cong_viec' in vals:
                    up_vals['taskss_name'] = vals['ten_cong_viec']

                if 'han_chot' in vals:
                    up_vals['deadline'] = vals['han_chot']

                if 'mo_ta' in vals:
                    up_vals['ly_do'] = vals['mo_ta']

                up_vals['progress'] = record.phan_tram_cong_viec

                if record.phan_tram_cong_viec == 0:
                    up_vals['status'] = 'todo'
                elif record.phan_tram_cong_viec < 100:
                    up_vals['status'] = 'doing'
                else:
                    up_vals['status'] = 'done'

                pm_task.with_context(skip_sync=True).write(up_vals)
        return res
    
    def unlink(self):
        if not self.env.context.get("skip_sync"):
            self.env["taskss"]\
                .search([("cong_viec_id", "in", self.ids)])\
                .with_context(skip_sync=True)\
                .unlink()

        return super().unlink()