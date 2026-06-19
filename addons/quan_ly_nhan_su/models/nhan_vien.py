from odoo import models, fields, api

class NhanVien(models.Model):
    _name = 'nhan_vien'
    _description = 'Bảng chứa thông tin nhân viên'
    _rec_name = 'display_name'

    ma_dinh_danh = fields.Char("Mã Định Danh")
    ngay_sinh = fields.Date("Ngày Sinh")  
    que_quan = fields.Char("Quê Quán")  
    email = fields.Char("Email") 
    gioi_tinh = fields.Selection(
        selection=[
            ('nam','Nam'),
            ('nu', 'Nữ'),
        ], 
        string="Giới Tính"
    )
    so_dien_thoai = fields.Char("Số Điện Thoại")  
    lich_su_lam_viec_ids = fields.One2many('lich_su_lam_viec', 'nhan_vien_id', string="Lịch Sử Làm Việc")
    nhom_du_an_ids = fields.Many2many('nhom_du_an', string='Nhóm Dự Án')
    
    du_an_ids = fields.Many2many('du_an', 'nhan_vien_du_an_rel', 'nhan_vien_id', 'du_an_id', string='Dự Án Đang Tham Gia')

    cong_viec_ids = fields.Many2many('cong_viec', 'nhan_vien_cong_viec_rel', 'nhan_vien_id', 'cong_viec_id', string='Công Việc Tham Gia')

    ho_va_ten = fields.Char("Họ và Tên", compute='_tinh_ho_va_ten', store=True)
    
    display_name = fields.Char(string='Tên Hiển Thị', compute='_compute_display_name', store=True)
    
    ho_ten_dem = fields.Char("Họ Tên Đệm")
    
    ten = fields.Char("Tên")
    
    chuc_vu_id = fields.Many2one("chuc_vu", string="Chức vụ", ondelete="set null") 
       
    _sql_constraints = [
        ('unique_email', 'UNIQUE(email)', 'Email đã tồn tại, vui lòng chọn email khác!')
    ]

    _sql_constraints = [
        ('unique_email', 'UNIQUE(email)', 'Email đã tồn tại, vui lòng chọn email khác!'),
        ('unique_ma_dinh_danh', 'UNIQUE(ma_dinh_danh)', 'Mã định danh đã tồn tại, vui lòng chọn mã khác!')
    ]

    @api.depends("ho_ten_dem", "ten")
    def _tinh_ho_va_ten(self):
        for record in self:
            if record.ho_ten_dem and record.ten:
                record.ho_va_ten = f"{record.ho_ten_dem} {record.ten}".strip()

    @api.onchange("ten", "ho_ten_dem")
    def _onchange_tinh_ma_dinh_danh(self):
        for record in self:
            if record.ho_ten_dem and record.ten:
                chu_cai_dau = ''.join([tu[0][0] for tu in record.ho_ten_dem.lower().split()])
                record.ma_dinh_danh = record.ten.lower() + chu_cai_dau
            else:
                record.ma_dinh_danh = False
                

    @api.depends('ho_va_ten', 'ma_dinh_danh')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.ho_va_ten} ({record.ma_dinh_danh})" if record.ma_dinh_danh else record.ho_va_ten
            
            
    
                
    