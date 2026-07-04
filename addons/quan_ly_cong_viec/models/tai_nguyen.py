from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TaiNguyen(models.Model):
    _name = 'tai_nguyen'
    _description = 'Tài Nguyên Dự Án'

    ten_tai_nguyen = fields.Char(string='Tên Tài Nguyên', required=True)
    so_luong = fields.Integer(string='Số Lượng', required=True, default=1)
    # du_an_id = fields.Many2one('du_an', string='Dự Án', ondelete='cascade')
        # SỬA DÒNG NÀY: Thêm domain lọc trạng thái dự án
    du_an_id = fields.Many2one(
        'du_an', 
        string='Dự Án', 
        required=True, 
        ondelete='cascade',
        domain="[('tien_do_du_an', 'not in', ['huy_bo', 'hoan_thanh'])]"
    )

    @api.constrains('du_an_id')
    def _check_du_an_tien_do(self):
        for record in self:
            if record.du_an_id and record.du_an_id.tien_do_du_an in ['hoan_thanh', 'huy_bo']:
                raise ValidationError("Không thể thêm hoặc gắn công việc vào dự án đã hoàn thành hoặc đã hủy bỏ.")
 