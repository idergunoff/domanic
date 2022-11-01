from load_data import *
from analysis_data import *
from classify_data import *


MainWindow.show()

ui.graphicsView.setBackground('w')
ui.graphicsView.showGrid(x=True, y=True)


def mouseMoved(evt):
    """ Отслеживаем координаты курсора и прокрутка таблицы до выбранного курсором значения """
    pos = evt[0]
    vb = ui.graphicsView.getPlotItem().vb
    if ui.graphicsView.sceneBoundingRect().contains(pos):
        mousePoint = vb.mapSceneToView(pos)
        ui.label_y.setText(str(round(mousePoint.x(), 3)))
        ui.label_x.setText(str(round(mousePoint.y(), 1)))
        items = ui.tableWidget.findItems(str(round(mousePoint.y(), 1)), QtCore.Qt.MatchExactly)
        if items:
            ui.tableWidget.scrollToItem(items[0])
            ui.tableWidget.setCurrentCell(items[0].row(), items[0].column())


def log_uncaught_exceptions(ex_cls, ex, tb):
    """ Вывод ошибок программы """
    text = '{}: {}:\n'.format(ex_cls.__name__, ex)
    text += ''.join(traceback.format_tb(tb))
    print(text)
    QtWidgets.QMessageBox.critical(None, 'Error', text)
    sys.exit()


proxy = pg.SignalProxy(ui.graphicsView.scene().sigMouseMoved, rateLimit=60, slot=mouseMoved)

ui.toolButton_add_region.clicked.connect(add_region)
ui.toolButton_add_area.clicked.connect(add_area)
ui.toolButton_add_well.clicked.connect(add_well)
ui.pushButton_las.clicked.connect(load_data_from_las)
ui.pushButton_pir.clicked.connect(load_data_pir)
ui.pushButton_pir_extr.clicked.connect(load_data_pir_extr)
ui.pushButton_chrom.clicked.connect(load_data_chrom)
ui.pushButton_chrom_extr.clicked.connect(load_data_chrom_extr)
ui.pushButton_depth.clicked.connect(load_depth_name)
ui.pushButton_lit.clicked.connect(load_data_lit)
ui.pushButton_del_param.clicked.connect(del_param)
ui.pushButton_add_param.clicked.connect(choice_param)
ui.pushButton_clear_param.clicked.connect(clear_param)
ui.pushButton_draw_param.clicked.connect(draw_sev_param)
ui.pushButton_norm_param.clicked.connect(draw_norm_sev_param)
ui.pushButton_table.clicked.connect(build_table_sev_param)
ui.pushButton_table_save.clicked.connect(save_table_sev_param)
ui.pushButton_add_param_rel.clicked.connect(add_param_for_relation)
ui.pushButton_clear_param_rel.clicked.connect(clear_param_relation)
ui.pushButton_draw_rel.clicked.connect(draw_relation)
ui.pushButton_rel_save.clicked.connect(save_relation)
ui.toolButton_add_class_lim.clicked.connect(add_class_lim)
ui.toolButton_del_class_lim.clicked.connect(del_class_lim)
ui.pushButton_add_param_class_lim.clicked.connect(add_param_for_class_lim)
ui.pushButton_del_param_class_lim.clicked.connect(del_param_for_class_lim)
ui.pushButton_calc_class_lim.clicked.connect(calc_class_lim)
ui.toolButton_add_class_lda.clicked.connect(add_class_lda)
ui.toolButton_del_class_lda.clicked.connect(del_class_lda)
ui.pushButton_add_int_lda.clicked.connect(add_int_lda)
ui.pushButton_add_param_class_lda.clicked.connect(add_param_for_LDA)
ui.pushButton_draw_lda.clicked.connect(draw_LDA)
ui.pushButton_clear_param_lda.clicked.connect(clear_list_param_lda)
ui.pushButton_lda_verify.clicked.connect(calc_verify_lda)
ui.pushButton_calc_class_lda.clicked.connect(calc_lda)
ui.pushButton_calc_resourse.clicked.connect(calc_resource)
ui.pushButton_table_resource.clicked.connect(save_table_resource)
ui.pushButton_clear_resourse.clicked.connect(del_category_to_resource)
ui.pushButton_add_constr.clicked.connect(add_constr)
ui.pushButton_clear_constr.clicked.connect(clear_constr)
ui.pushButton_calc_constr.clicked.connect(calc_constr)
ui.pushButton_del_param_rel.clicked.connect(del_param_rel)
ui.pushButton_del_param_srav.clicked.connect(del_param_srav)
ui.pushButton_add_param_corr.clicked.connect(add_param_corr)
ui.pushButton_add_tab_corr.clicked.connect(add_all_param_corr)
ui.pushButton_del_param_corr.clicked.connect(del_param_corr)
ui.pushButton_clear_param_corr.clicked.connect(clear_param_corr)
ui.pushButton_calc_corr.clicked.connect(calc_corr)

ui.comboBox_region.activated.connect(comboBox_area_update)
ui.comboBox_area.activated.connect(comboBox_well_update)
ui.comboBox_well.activated.connect(well_interval)
ui.comboBox_color.activated.connect(set_style_combobox)
ui.comboBox_dash.activated.connect(set_style_combobox)
ui.comboBox_width.activated.connect(set_style_combobox)
ui.comboBox_class_lim.activated.connect(display_param_limits)
ui.comboBox_class_lda.activated.connect(comboBox_class_lda_cat_update)
ui.comboBox_class_lda.activated.connect(reset_fake_lda)

ui.doubleSpinBox_start.valueChanged.connect(update_interval)
ui.doubleSpinBox_stop.valueChanged.connect(update_interval)

ui.listWidget_las.itemSelectionChanged.connect(draw_param_las)
ui.listWidget_pir_kern.itemSelectionChanged.connect(draw_param_pir_kern)
ui.listWidget_pir_extr.itemSelectionChanged.connect(draw_param_pir_extr)
ui.listWidget_chrom_kern.itemSelectionChanged.connect(draw_param_chrom_kern)
ui.listWidget_chrom_extr.itemSelectionChanged.connect(draw_param_chrom_extr)
ui.listWidget_lit.itemSelectionChanged.connect(draw_param_lit)

ui.tableWidget.clicked.connect(click_table)



reset_fake_lda()
comboBox_region_update()
set_style_combobox()
clear_param()
comboBox_class_lda_update()
comboBox_class_lim_update()
display_param_limits()
comboBox_class_lda_cat_update()


sys.excepthook = log_uncaught_exceptions

sys.exit(app.exec_())
