# from odoo import models, fields

# class NhomDuAn(models.Model):
#     _name = 'nhom_du_an'
#     _description = 'Nhóm Dự Án'
#     _rec_name = 'ten_nhom'

#     ten_nhom = fields.Char(string='Tên Nhóm')
#     nhan_vien_ids = fields.Many2many('nhan_vien', string='Thành Viên')
    
    
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class NhomDuAn(models.Model):
    _name = 'nhom_du_an'
    _description = 'Nhóm Dự Án'
    _rec_name = 'ten_nhom'

    ten_nhom = fields.Char(
        string='Tên Nhóm',
        required=True
    )

    truong_nhom_id = fields.Many2one(
        'nhan_vien',
        string='Trưởng nhóm'
    )

    nhan_vien_ids = fields.Many2many(
        'nhan_vien',
        string='Thành viên'
    )

    @api.onchange('truong_nhom_id')
    def _onchange_truong_nhom(self):
        """
        Khi chọn trưởng nhóm thì tự thêm vào danh sách thành viên.
        """
        if self.truong_nhom_id:
            self.nhan_vien_ids = [(4, self.truong_nhom_id.id)]

    @api.constrains('truong_nhom_id', 'nhan_vien_ids')
    def _check_truong_nhom(self):
        for record in self:
            if (
                record.truong_nhom_id
                and record.truong_nhom_id not in record.nhan_vien_ids
            ):
                raise ValidationError(
                    "Trưởng nhóm phải là thành viên của nhóm."
                )