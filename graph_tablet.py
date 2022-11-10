from functions import *




def set_style_combobox_tablet():
    """ Установка выбранного цвета фоном комбобокса (выпадающего списка) """
    color = choice_color_tablet()
    color = 'grey' if color == 'black' else color
    ui.comboBox_color_tablet.setStyleSheet(f"background-color: {color};")


def add_param_tablet():
    """ Добавление параметра в список для графического планшета """
    table, table_text, widget = check_tabWidjet()
    try:
        param = widget.currentItem().text()
        color = choice_color_tablet()
        new_param_tablet = DrawGraphTablet(well_id=get_well_id(), table=table_text, param=param, color=color,
                                     dash=' '.join(list(map(str, choice_dash_tablet()))), width=choice_width_tablet(),
                                           type_graph=ui.comboBox_type_graph.currentText())
        session.add(new_param_tablet)  # параметр добавляется в отдельную таблицу + параметры графика
        session.commit()
        show_list_tablet()
    except AttributeError:
        ui.label_info.setText(f'Внимание! Не выбран параметр.')
        ui.label_info.setStyleSheet('color: red')


def add_next_graph():
    """ Добавление нового графика для графического планшета """
    new_param_tablet = DrawGraphTablet(well_id=get_well_id(), table='', param='', color='',
                                       dash='', width='', type_graph='')
    session.add(new_param_tablet)  # параметр добавляется в отдельную таблицу + параметры графика
    session.commit()
    show_list_tablet()


def clear_param_tablet():
    """ Очистка списка выбранных параметров графического планшета """
    ui.listWidget_param_tablet.clear()
    session.query(DrawGraphTablet).delete()
    session.commit()


def del_param_tablet():
    """ Удалить выбранный параметр планшета """
    try:
        current_param_text = ui.listWidget_param_tablet.currentItem().text()
        id_param = current_param_text.split(' ')[0]
        session.query(DrawGraphTablet).filter(DrawGraphTablet.id == id_param).delete()
        session.commit()
        show_list_tablet()
    except AttributeError:
        ui.label_info.setText(f'Параметр не выбран.')
        ui.label_info.setStyleSheet('color: red')


def edit_param_tablet():
    """ Изменене  параметра в списке для графического планшета """
    try:
        current_param_text = ui.listWidget_param_tablet.currentItem().text()
        id_param = current_param_text.split(' ')[0]
        session.query(DrawGraphTablet).filter(DrawGraphTablet.id == id_param).update({'color': choice_color_tablet(),
            'dash': ' '.join(list(map(str, choice_dash_tablet()))), 'width': choice_width_tablet(),
            'type_graph': ui.comboBox_type_graph.currentText()}, synchronize_session="fetch")
        session.commit()
        show_list_tablet()
    except AttributeError:
        ui.label_info.setText(f'Параметр не выбран.')
        ui.label_info.setStyleSheet('color: red')


def draw_graph_tablet():
    """ Отрисовка всех графиков на планшете """

    params_graph_tablet = session.query(DrawGraphTablet).all()
    count_graph = session.query(DrawGraphTablet).filter(DrawGraphTablet.param == '').count() + 1
    fig = plt.figure(figsize=(2 * count_graph, 9))

    min_Y, max_Y = check_start_stop()
    min_depth, max_depth = get_min_max_tablet_graph()
    min_Y = min_Y if min_Y > min_depth else min_depth
    max_Y = max_Y if max_Y < max_depth else max_depth

    n, n_graph = 0, 1
    for i in params_graph_tablet:
        if i.param:
            add_graph_tablet(i, min_Y, max_Y, count_graph, n_graph, fig, n)
            n += 1
        else:
            n_graph += 1
            n = 0


    fig.tight_layout()
    fig.show()


def add_graph_tablet(param_row, min_Y, max_Y, count_graph, n_graph, fig, n):
    """ Добавляем график на планшет """
    table = get_table(param_row.table)
    X = sum(list(map(list, session.query(literal_column(f'{param_row.table}.{param_row.param}')).filter(table.well_id == param_row.well_id,
                                     literal_column(f'{param_row.table}.{param_row.param}') != None,
                                        table.depth >= min_Y, table.depth <= max_Y).order_by(table.depth).all())), [])
    Y = sum(list(map(list, session.query(table.depth).filter(table.well_id == param_row.well_id,
                                     literal_column(f'{param_row.table}.{param_row.param}') != None,
                                         table.depth >= min_Y, table.depth <= max_Y).order_by(table.depth).all())), [])

    ax = fig.add_subplot(1, count_graph, n_graph)
    ax.grid(axis='x', color=param_row.color, lw=0.5, ls=':')
    ax.grid(axis='y', lw=0.5, ls=':')
    ax.patch.set_alpha(0)
    if param_row.table == 'data_las':
        ax.plot(X, Y, c=param_row.color, lw=param_row.width, ls=get_dash(param_row.dash))
    else:
        if param_row.type_graph == 'bar':
            ax.barh(Y, X, color=param_row.color, height=float(param_row.width)*0.1)
        else:
            try:
                ax.stem(Y, X, orientation='horizontal', linefmt=(get_dash(param_row.dash), param_row.color),
                    markerfmt=(get_marker(param_row.dash), param_row.color), basefmt=('black'))
            except TypeError:
                ui.label_info.setText(f'Графики формата "stem" не принимают оттенки цветов (с приставкой dark и light)')
                ui.label_info.setStyleSheet('color: red')
    height_grapf = max_Y - min_Y
    plt.ylim(min_Y - height_grapf / 100, max_Y + height_grapf / 100)

    tkw = dict(size=4, width=1.5)
    ax.tick_params(axis='x', color=param_row.color, labelcolor=param_row.color, **tkw)


    ax.set_xlabel(param_row.param, color=param_row.color)
    ax.spines.top.set_position(("axes", 1+n*0.07))
    ax.spines.top.set(color=param_row.color)
    ax.axes.xaxis.tick_top()
    ax.axes.xaxis.set_label_position("top")
    ax.axes.xaxis.set_ticks_position("top")


    if count_graph > n_graph > 1:
        ax.axes.yaxis.set_ticklabels([])
    if n_graph == count_graph:
        ax.axes.yaxis.set_label_position("right")
        ax.axes.yaxis.tick_right()
    ax.invert_yaxis()


# def draw_total_cement(device, n_izm, n_graph, fig, count_sig):
#     """ функция отрисовки цементограммы по всей длине """
#     if device is all_signals_old:
#         int_min_self = int_min_old
#         int_max_self = int_max_old
#     else:
#         int_min_self = int_min
#         int_max_self = int_max
#     depth = device['depth'].iloc[int_min_self:int_max_self].tolist()
#     curve = device[str(n_izm) + '_diff_result'].iloc[int_min_self:int_max_self].tolist()
#     if device is all_signals:
#         if ui.checkBox_gen_def_new.checkState() == 2:
#             quality = np.array(device[str(n_izm) + '_qual_mean'].iloc[int_min_self:int_max_self].tolist())
#         else:
#             quality = np.array(device[str(n_izm) + '_quality'].iloc[int_min_self:int_max_self].tolist())
#     else:
#         if ui.checkBox_gen_def_old.checkState() == 2:
#             quality = np.array(device[str(n_izm) + '_qual_mean'].iloc[int_min_self:int_max_self].tolist())
#         else:
#             quality = np.array(device[str(n_izm) + '_quality'].iloc[int_min_self:int_max_self].tolist())
#     max_depth = np.max(depth)
#     min_depth = np.min(depth)
#     min_value = np.min(curve)
#     max_value = np.max(curve)
#     min_cement = min_value - (10 * (max_value - min_value) / 100)
#     max_cement = max_value + (10 * (max_value - min_value) / 100)
#     if device is all_signals:
#         if ui.checkBox_gen_def_new.checkState() == 2:
#             defect1 = ui.doubleSpinBox_defect1_new.value()
#             defect2 = ui.doubleSpinBox_defect2_new.value()
#         else:
#             defect1 = min_value + (max_value - min_value) / 3
#             defect2 = min_value + (2 * (max_value - min_value) / 3)
#     else:
#         if ui.checkBox_gen_def_old.checkState() == 2:
#             defect1 = ui.doubleSpinBox_defect1_old.value()
#             defect2 = ui.doubleSpinBox_defect2_old.value()
#         else:
#             defect1 = min_value + (max_value - min_value) / 3
#             defect2 = min_value + (2 * (max_value - min_value) / 3)
#     ax = fig.add_subplot(1, count_sig, n_graph)
#     ax.axvline(x=defect1, linewidth=0.5, color='black', linestyle=':')
#     ax.axvline(x=defect2, linewidth=0.5, color='black', linestyle=':')
#     ax.fill_betweenx(depth, max_cement, curve, where=quality >= 1, hatch='//', facecolor='#EDEDED')
#     ax.fill_betweenx(depth, max_cement, curve, where=quality >= 2, hatch='\\\\\\\\', facecolor='#BDBDBD')
#     ax.fill_betweenx(depth, min_cement, curve, where=quality >= 1, hatch='//', facecolor='#EDEDED')
#     ax.fill_betweenx(depth, min_cement, curve, where=quality >= 2, hatch='\\\\\\\\', facecolor='#BDBDBD')
#     ax.plot(curve, depth, 'black')
#     plt.ylim(min_depth, max_depth)
#     plt.xlim(min_cement, max_cement)
#     if device is all_signals:
#         plt.title(all_stat['name'][n_izm][-35:-23])
#     if device is all_signals_old:
#         plt.title(all_stat_old['name'][n_izm])
#     ax.get_xaxis().set_visible(False)
#     plt.yticks(np.arange(min_depth, max_depth, 5))
#     ax.grid(axis='y', color='black', linestyle=':', linewidth=0.5)
#
#     ui.label_info.setText('Готово!')
#     ui.label_info.setStyleSheet('color:green')