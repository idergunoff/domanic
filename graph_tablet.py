from functions import *


def change_color_tablet():
    button_color = ui.pushButton_color_tablet.palette().color(ui.pushButton_color_tablet.backgroundRole())
    color = QColorDialog.getColor(button_color)
    ui.pushButton_color_tablet.setStyleSheet(f"background-color: {color.name()};")
    # ui.pushButton_color.setText(color.name())



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
    gs = GridSpec(1, count_graph + 1, width_ratios=[1] + [3] * count_graph)

    min_Y, max_Y = check_start_stop()
    min_depth, max_depth = get_min_max_tablet_graph()
    min_Y = min_Y if min_Y > min_depth else min_depth
    max_Y = max_Y if max_Y < max_depth else max_depth

    ax0 = fig.add_subplot(gs[0])

    age = session.query(DataAge).filter(
        DataAge.well_id == params_graph_tablet[0].well_id,
        DataAge.depth >= min_Y,
        DataAge.depth <= max_Y
    ).order_by(DataAge.depth).all()
    list_data_age = extract_intervals(age)
    for i in list_data_age:
        if i['start'] != min_Y:
            ax0.axhline(i['start'], color='black', linewidth=1.5)
        if i['stop'] != max_Y:
            ax0.axhline(i['stop'], color='black', linewidth=1.5)
        ax0.text(0.5, (i['start'] + i['stop']) / 2, i['age_name'], ha='center', va='center', rotation=90)
    height_grapf = max_Y - min_Y # высота графика
    plt.ylim(min_Y - height_grapf / 100, max_Y + height_grapf / 100) # установка границ графика
    ax0.invert_yaxis()

    ax0.set_title('  Горизонт', rotation=90)
    ax0.spines.top.set_position(("axes", 1))
    ax0.axes.xaxis.tick_top()
    ax0.axes.xaxis.set_ticks_position("top")
    ax0.axes.xaxis.set_ticklabels([])

    n, n_graph = 0, 1
    for i in params_graph_tablet:
        if i.param:
            interval = True if n == 0 and ui.checkBox_tablet_interval.isChecked() else False
            add_graph_tablet(gs, i, min_Y, max_Y, count_graph, n_graph, fig, n, interval)
            n += 1
        else:
            n_graph += 1
            n = 0

    fig.tight_layout()
    plt.subplots_adjust(wspace=0.2)
    fig.show()


def add_graph_tablet(gs, param_row, min_Y, max_Y, count_graph, n_graph, fig, n, interval):
    """
    Добавление графика для графического планшета
    :param param_row: выбранный параметр
    :param min_Y: минимальная глубина параметра
    :param max_Y: максимальная глубина параметра
    :param count_graph: количество графиков
    :param n_graph: номер графика
    :param fig: фигура планшета
    :param n: номер графика
    :param interval: отображать интервалы
    :return:
    """


    table = get_table(param_row.table)
    X = sum(list(map(list, session.query(literal_column(f'{param_row.table}.{param_row.param}')).filter(
        table.well_id == param_row.well_id,
        literal_column(f'{param_row.table}.{param_row.param}') != None,
        table.depth >= min_Y,
        table.depth <= max_Y
    ).order_by(table.depth).all())), [])
    Y = sum(list(map(list, session.query(table.depth).filter(
        table.well_id == param_row.well_id,
        literal_column(f'{param_row.table}.{param_row.param}') != None,
        table.depth >= min_Y,
        table.depth <= max_Y
    ).order_by(table.depth).all())), [])

    # ax = fig.add_subplot(1, count_graph, n_graph)
    ax = fig.add_subplot(gs[n_graph])
    ax.grid(axis='x', color=param_row.color, lw=0.5, ls=':')
    ax.grid(axis='y', lw=0.5, ls=':')
    ax.patch.set_alpha(0) # убираем прозрачность
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
    height_grapf = max_Y - min_Y # высота графика
    plt.ylim(min_Y - height_grapf / 100, max_Y + height_grapf / 100) # установка границ графика

    tkw = dict(size=4, width=1.5)
    ax.tick_params(axis='x', color=param_row.color, labelcolor=param_row.color, **tkw)


    ax.set_xlabel(param_row.param, color=param_row.color)
    ax.spines.top.set_position(("axes", 1+n*0.07))
    ax.spines.top.set(color=param_row.color)
    ax.axes.xaxis.tick_top()
    ax.axes.xaxis.set_label_position("top")
    ax.axes.xaxis.set_ticks_position("top")


    if count_graph > n_graph > 0:
        ax.axes.yaxis.set_ticklabels([]) # Убираем подписи оси Y на всех графиках, кроме последнего
    if n_graph == count_graph:
        ax.axes.yaxis.set_label_position("right")
        ax.axes.yaxis.tick_right()
    ax.invert_yaxis()

    if interval:
        xlim_ax = ax.get_xlim()
        for i in range(ui.listWidget_user_int.count()):
            item = ui.listWidget_user_int.item(i)
            if isinstance(item, QListWidgetItem):
                checkbox = ui.listWidget_user_int.itemWidget(item)
                if isinstance(checkbox, QCheckBox) and checkbox.isChecked():
                    user_int = session.query(UserInterval).filter_by(id=checkbox.property('interval_id')).first()

                    y1 = user_int.int_from  # Значение y1, начало заливки
                    y2 = user_int.int_to  # Значение y2, конец заливки

                    # Задаем прямоугольную область для заливки
                    ax.fill_betweenx([y1, y2], xlim_ax[0], xlim_ax[1], alpha=0.5, color=user_int.color)

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


def extract_intervals(data):
    # Инициализируем пустой список для хранения результата
    result = []

    # Инициализируем переменную для хранения текущего интервала
    current_interval = None

    # Проходим по каждому элементу во входных данных
    for item in data:
        # Если текущий интервал пустой или название возраста (age) отличается от предыдущего интервала
        if current_interval is None or item.age != current_interval['age_name']:
            # Если текущий интервал не пустой (это означает, что мы закончили предыдущий интервал), то добавляем его в результат
            if current_interval is not None:
                result.append({
                    'start': current_interval['start'],
                    'stop': current_interval['stop'],
                    'age_name': current_interval['age_name']
                })

            # Создаем новый текущий интервал с начальной и конечной глубиной и названием возраста
            current_interval = {
                'start': item.depth,
                'stop': item.depth,
                'age_name': item.age
            }
        else:
            # Если название возраста совпадает с предыдущим интервалом, обновляем конечную глубину текущего интервала
            current_interval['stop'] = item.depth

    # После завершения цикла добавляем последний интервал (если таковой существует) в результат
    if current_interval is not None:
        result.append({
            'start': current_interval['start'],
            'stop': current_interval['stop'],
            'age_name': current_interval['age_name']
        })

    # Возвращаем список интервалов
    return result


def update_template_graph_tablet():
    ui.comboBox_temp_graph_tab.clear()
    for i in session.query(TemplateGraphTablet).all():
        ui.comboBox_temp_graph_tab.addItem(f'{i.title} id{i.id}')


def add_template_graph_tablet():
    params_graph_tablet = session.query(DrawGraphTablet).all()
    title = ui.lineEdit_string.text()
    if title != '':
        session.add(TemplateGraphTablet(
            title=title,
            table=json.dumps([i.table for i in params_graph_tablet]),
            param=json.dumps([i.param for i in params_graph_tablet]),
            color=json.dumps([i.color for i in params_graph_tablet]),
            dash=json.dumps([i.dash for i in params_graph_tablet]),
            width=json.dumps([i.width for i in params_graph_tablet]),
            type_graph=json.dumps([i.type_graph for i in params_graph_tablet])
        ))
        session.commit()
        update_template_graph_tablet()
    else:
        ui.label_info.setText('Введите название шаблона')
        ui.label_info.setStyleSheet('color: red')


def delete_template_graph_tablet():
    session.query(TemplateGraphTablet).filter_by(id=ui.comboBox_temp_graph_tab.currentText().split(' id')[-1]).delete()
    session.commit()
    update_template_graph_tablet()


def use_template_graph_tablet():
    clear_param_tablet()
    temp_graph_tab = session.query(TemplateGraphTablet).filter_by(id=ui.comboBox_temp_graph_tab.currentText().split(' id')[-1]).first()
    table = json.loads(temp_graph_tab.table)
    param = json.loads(temp_graph_tab.param)
    color = json.loads(temp_graph_tab.color)
    dash = json.loads(temp_graph_tab.dash)
    width = json.loads(temp_graph_tab.width)
    type_graph = json.loads(temp_graph_tab.type_graph)
    for i in range(len(table)):
        new_param_tablet = DrawGraphTablet(well_id=get_well_id(), table=table[i], param=param[i], color=color[i],
                                           dash=dash[i], width=width[i], type_graph=type_graph[i])
        session.add(new_param_tablet)  # параметр добавляется в отдельную таблицу + параметры графика
        session.commit()
    show_list_tablet()

