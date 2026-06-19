from odoo import models, fields

class NhomDuAn(models.Model):
    _name = 'nhom_du_an'
    _description = 'Nhóm Dự Án'
    _rec_name = 'ten_nhom'

    ten_nhom = fields.Char(string='Tên Nhóm')
    nhan_vien_ids = fields.Many2many('nhan_vien', string='Thành Viên')
    
    
