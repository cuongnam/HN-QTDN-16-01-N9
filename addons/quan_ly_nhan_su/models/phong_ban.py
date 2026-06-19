from odoo import models, fields, api
class PhongBan(models.Model):
    _name = 'phong_ban'
    _description = 'Phòng ban của nhân viên'

    ma_phong_ban = fields.Char("Mã phòng ban", reuired=True)
    ten_phong_ban = fields.Char("Tên phòng ban", required=True)

    nhan_vien_ids = fields.Many2one('nhan_vien',  string="Nhân viên")
    # lich_su_lam_viec_ids = fields.One2many('lich_su_lam_viec', inverse_name='ma_phong_ban', string='Danh sách Phòng ban')

    def name_get(self):
        result = []
        for record in self:
            name = record.ten_phong_ban
            result.append((record.id, name))
        return result