from load_data import *
from analysis_data import *
from classify_data import *
from graph_tablet import *
from user_interval import *
from compare_interval import *
from regression import *
from calculated_data import *

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

ui.toolButton_int_reset.clicked.connect(well_interval)
ui.pushButton_color.clicked.connect(change_color)
ui.toolButton_add_region.clicked.connect(add_region)
ui.toolButton_add_area.clicked.connect(add_area)
ui.toolButton_add_well.clicked.connect(add_well)
ui.pushButton_las.clicked.connect(load_data_from_las)
ui.pushButton_pir.clicked.connect(load_data_pir)
ui.pushButton_pir_extr.clicked.connect(load_data_pir_extr)
ui.pushButton_chrom.clicked.connect(load_data_chrom)
ui.pushButton_chrom_extr.clicked.connect(load_data_chrom_extr)
ui.pushButton_depth.clicked.connect(load_depth_name)
ui.pushButton_add_age.clicked.connect(load_age)
ui.pushButton_lit.clicked.connect(load_data_lit)


ui.pushButton_del_param.clicked.connect(del_param)
ui.pushButton_add_param.clicked.connect(choice_param)
ui.pushButton_add_param_ml.clicked.connect(add_param_ml)
ui.pushButton_add_all_param.clicked.connect(choice_all_param)
ui.pushButton_clear_param.clicked.connect(clear_param)
ui.pushButton_draw_param.clicked.connect(draw_sev_param)
ui.pushButton_norm_param.clicked.connect(draw_norm_sev_param)
ui.pushButton_table.clicked.connect(build_table_sev_param)
ui.pushButton_table_save.clicked.connect(save_table_sev_param)
ui.pushButton_add_param_rel.clicked.connect(add_param_for_relation)
ui.pushButton_add_param_ml_rel.clicked.connect(add_param_ml_for_relation)
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
ui.pushButton_add_param_res.clicked.connect(add_param_resource)
ui.pushButton_add_tab_res.clicked.connect(add_all_param_resource)
ui.pushButton_clear_param_res.clicked.connect(clear_param_resource)
ui.pushButton_del_param_res.clicked.connect(del_param_resource)

# graph tablet
ui.pushButton_add_param_tablet.clicked.connect(add_param_tablet)
ui.pushButton_edit_param_tablet.clicked.connect(edit_param_tablet)
ui.pushButton_clear_param_tablet.clicked.connect(clear_param_tablet)
ui.pushButton_del_param_tablet.clicked.connect(del_param_tablet)
ui.pushButton_draw_param_tablet.clicked.connect(draw_graph_tablet)
ui.pushButton_next_graph_tablet.clicked.connect(add_next_graph)
ui.pushButton_color_tablet.clicked.connect(change_color_tablet)
ui.pushButton_add_temp_graph_tab.clicked.connect(add_template_graph_tablet)
ui.pushButton_del_temp_graph_tab.clicked.connect(delete_template_graph_tablet)
ui.pushButton_use_temp_graph_tab.clicked.connect(use_template_graph_tablet)


ui.pushButton_rel_color.clicked.connect(set_style_pushbutton_color)

ui.comboBox_region.currentIndexChanged.connect(comboBox_area_update)
ui.comboBox_area.currentIndexChanged.connect(comboBox_well_update)
ui.comboBox_well.currentIndexChanged.connect(well_interval)
# ui.comboBox_color.activated.connect(set_style_combobox)
ui.comboBox_dash.activated.connect(draw_current_graph_by_style)
ui.comboBox_width.activated.connect(draw_current_graph_by_style)
# ui.comboBox_color_tablet.activated.connect(set_style_combobox_tablet)
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

# user interval
ui.pushButton_add_user_int.clicked.connect(add_user_interval)
ui.pushButton_add_from_cat_user_int.clicked.connect(add_user_interval_from_category)
ui.pushButton_edit_user_int.clicked.connect(edit_user_interval)
ui.pushButton_del_user_int.clicked.connect(delete_user_interval)
ui.pushButton_to_work_user_int.clicked.connect(user_interval_to_work)
ui.checkBox_choose_all_user_int.clicked.connect(choose_all_user_interval)

# compare interval
ui.pushButton_compare_add_int.clicked.connect(add_compare_interval)
ui.pushButton_compare_add_param.clicked.connect(add_compare_parameter)
ui.pushButton_compare_del_int.clicked.connect(delete_compare_interval)
ui.pushButton_compare_del_param.clicked.connect(delete_compare_parameter)
ui.pushButton_compare_clear_int.clicked.connect(clear_compare_interval)
ui.pushButton_compare_clear_param.clicked.connect(clear_compare_parameter)
ui.pushButton_compare_draw.clicked.connect(draw_compare_interval)
ui.pushButton_compare_matrix.clicked.connect(matrix_compare_interval)
ui.pushButton_compare_table.clicked.connect(table_compare_interval)
ui.pushButton_compare_save.clicked.connect(save_compare_interval)

# regression analysis
ui.toolButton_add_reg_an.clicked.connect(add_regression_analysis)
ui.toolButton_del_reg_an.clicked.connect(remove_regression_analysis)
ui.comboBox_reg_analysis.activated.connect(update_list_regression_well)
ui.comboBox_reg_analysis.activated.connect(update_list_features_regression)
ui.comboBox_reg_analysis.activated.connect(set_target_param)
ui.listWidget_reg_param.itemSelectionChanged.connect(show_features_regression)
ui.toolButton_update_target_param.clicked.connect(update_new_target_param)
ui.toolButton_add_reg_well.clicked.connect(add_regression_well)
ui.toolButton_del_reg_well.clicked.connect(remove_regression_well)
ui.pushButton_add_reg_param.clicked.connect(add_feature_regression)
ui.pushButton_del_reg_param.clicked.connect(remove_feature_regression)
ui.pushButton_add_reg_all_param.clicked.connect(add_all_table_to_features_regression)
ui.pushButton_clear_reg_param.clicked.connect(clear_list_features_regression)
ui.pushButton_model_reg.clicked.connect(train_regression_model)
ui.pushButton_del_reg_model.clicked.connect(remove_trained_regression_model)
ui.pushButton_calc_reg_model.clicked.connect(calc_regression_model)
ui.pushButton_trained_models_comment.clicked.connect(update_trained_model_comment)

# calculated data
ui.listWidget_calc_data.itemSelectionChanged.connect(show_calc_data)
ui.pushButton_del_calc_data.clicked.connect(delete_calc_data)
ui.pushButton_cut_calc_data.clicked.connect(cut_calc_data)

reset_fake_lda()
comboBox_region_update()
draw_current_graph_by_style()
# set_style_combobox_tablet()
clear_param()
clear_param_tablet()
comboBox_class_lda_update()
comboBox_class_lim_update()
display_param_limits()
comboBox_class_lda_cat_update()
for button in [ui.pushButton_color, ui.pushButton_color_tablet, ui.pushButton_rel_color]:
    set_random_color(button)
user_interval_list_update()
update_list_compare_interval()
add_stat_checkbox()
update_template_graph_tablet()
update_list_regression_analysis()
update_list_trained_regression_models()
update_list_calculated_data()

sys.excepthook = log_uncaught_exceptions

sys.exit(app.exec_())
