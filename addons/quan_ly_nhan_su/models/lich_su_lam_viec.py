from odoo import models, fields

class LichSuLamViec(models.Model):
    _name = 'lich_su_lam_viec'
    _description = 'Bảng chứa thông tin Lịch sử làm việc'
    _rec_name = 'ten_lich_su'

    ten_lich_su = fields.Char("Tên Lịch Sử")
    nhan_vien_id = fields.Many2one("nhan_vien", string="Nhân Viên", ondelete='cascade')
    chuc_vu_id = fields.Many2one("chuc_vu", string="Chức Vụ", related="nhan_vien_id.chuc_vu_id", store=True, readonly=True)
