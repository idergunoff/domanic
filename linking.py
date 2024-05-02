import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PyQt5.QtCore import QModelIndex

from functions import *


def remove_linking():
    """ Удаление привязки """
    curr_linking = session.query(Linking).filter_by(id=get_linking_id()).first()
    if curr_linking:
        name_linking = f'{curr_linking.table_curve}({curr_linking.param_curve}) - {curr_linking.table_sample}({curr_linking.param_sample})'
    else:
        return
    result = QtWidgets.QMessageBox.question(
        MainWindow, 'Удаление привязки', f'Вы действительно хотите удалить привязку "{name_linking}"?',
        QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No
    )
    if result == QtWidgets.QMessageBox.No:
        return
    else:
        # todo: удалить все данные из trying и sample, которые связаны с этой привязкой, отмена всех сдвигов если они были применены

        for i in session.query(Trying).filter_by(linking_id=curr_linking.id).all():
            session.query(Shift).filter_by(trying_id=i.id).delete()

        session.query(Trying).filter_by(linking_id=curr_linking.id).delete()
        session.query(Sample).filter_by(linking_id=curr_linking.id).delete()
        session.delete(curr_linking)
        session.commit()
        update_combobox_linking()
        set_label_info(f'Привязка "{name_linking}" удалена.', 'green')


def add_linking():
    """ Добавление привязки """
    if not ui.listWidget_relation.count() == 2:
        QMessageBox.critical(MainWindow, 'Внимание', 'Необходимо выбрать два параметра для привязки на вкладке 2 '
                                                     'в разделе Зависимости.')
        return
    table_curve, param_curve, table_sample, param_sample = '', '', '', ''
    for i in range(2):
        text = ui.listWidget_relation.item(i).text()
        if text.split()[1] == 'data_las':
            table_curve, param_curve = text.split()[1], text.split()[0]
        else:
            table_sample, param_sample = text.split()[1], text.split()[0]
    if table_curve == '' or table_sample == '' or param_curve == '' or param_sample == '':
        QMessageBox.critical(MainWindow, 'Внимание', 'Один из параметров должен быть обязательно из таблицв LAS, '
                                                     'второй обязательно не из таблицы LAS.')
        return

    new_linking = Linking(
        well_id=get_well_id(),
        table_curve=table_curve,
        param_curve=param_curve,
        table_sample=table_sample,
        param_sample=param_sample
    )

    session.add(new_linking)
    session.commit()
    update_combobox_linking()
    add_samples_to_linking()



def add_samples_to_linking():
    """ Добавление образцов в привязку """
    curr_link = session.query(Linking).filter_by(id=get_linking_id()).first()
    session.query(Sample).filter_by(linking_id=curr_link.id).delete()
    session.commit()
    t_curve = get_table(curr_link.table_curve)
    t_sample = get_table(curr_link.table_sample)
    samples = session.query(
        t_sample.depth, literal_column(f'{curr_link.table_sample}.{curr_link.param_sample}')
    ).filter(
        t_sample.well_id == curr_link.well_id,
        # t_sample.depth >= ui.doubleSpinBox_start.value(),
        # t_sample.depth <= ui.doubleSpinBox_stop.value(),
        literal_column(f'{curr_link.table_sample}.{curr_link.param_sample}').isnot(None)
    ).order_by(t_sample.depth).all()
    for s in samples:
        curve_val = session.query(t_curve).filter(
            t_curve.well_id == curr_link.well_id,
            t_curve.depth >= round(s[0], 1),
            t_curve.depth < round(s[0], 1) + 0.1,
            literal_column(f'{curr_link.table_curve}.{curr_link.param_curve}').isnot(None)
        ).first()
        if curve_val:
            new_sample = Sample(
                depth=int(s[0] * 10) / 10,
                value=s[1],
                linking_id=curr_link.id
            )
            session.add(new_sample)
    session.commit()
    update_listwidget_samples()


def add_samples_to_skip_by_interval(start_depth, stop_depth, trying):
    for s in trying.linking.samples:
        if s.depth < start_depth or s.depth >= stop_depth:
            new_skip_sample = SkipSample(trying_id=trying.id, sample_id=s.id)
            session.add(new_skip_sample)
    session.commit()


def add_sample_to_skip():
    trying = session.query(Trying).filter_by(id=get_trying_id()).first()
    if trying.corr:
        result = QMessageBox.question(MainWindow, 'Внимание', 'Сдвиги привязки уже рассчитаны. При изменении списка '
                                                              'исключений все расчеты будут сброшены. Продолжить?',
                                      QMessageBox.Yes | QMessageBox.No)
        if result == QMessageBox.No:
            return
        else:
            trying.corr = None
            trying.old_corr = None
            trying.shift_value = None
            for i in trying.shifts:
                session.delete(i)
            session.commit()
            update_listwidget_trying()
            for i in range(ui.listWidget_trying.count()):
                if int(ui.listWidget_trying.item(i).text().split(' id')[-1]) == trying.id:
                    ui.listWidget_trying.setCurrentRow(i)
    skip = session.query(SkipSample).filter_by(trying_id=get_trying_id(), sample_id=get_sample_id()).first()
    if skip:
        session.delete(skip)
    else:
        new_skip_sample = SkipSample(trying_id=get_trying_id(), sample_id=get_sample_id())
        session.add(new_skip_sample)
    session.commit()
    update_listwidget_samples_for_trying()
    draw_result_linking()



def add_new_trying():
    new_trying = Trying(
        linking_id=get_linking_id(),
        up_depth=round(ui.doubleSpinBox_start.value(), 1),
        down_depth=round(ui.doubleSpinBox_stop.value(), 1),
        algorithm=ui.comboBox_opt_algorithm.currentText(),
        method_shift=ui.comboBox_shift_method.currentText(),
        n_iter=ui.spinBox_n_iter_linking.value(),
        limit=round(ui.doubleSpinBox_lim_shift.value(), 1),
        bin=ui.spinBox_linking_bin.value()
    )
    session.add(new_trying)
    session.commit()

    start, stop = check_start_stop()
    add_samples_to_skip_by_interval(start, stop, new_trying)
    update_listwidget_trying()


def calc_linking():
    """ Расчет привязки """
    curr_link = session.query(Linking).filter_by(id=get_linking_id()).first()
    start, stop = check_start_stop()
    t_curve = get_table(curr_link.table_curve)
    curve = session.query(
        t_curve.depth, literal_column(f'{curr_link.table_curve}.{curr_link.param_curve}')
    ).filter(
        t_curve.well_id == curr_link.well_id,
        literal_column(f'{curr_link.table_curve}.{curr_link.param_curve}').isnot(None)
    ).order_by(t_curve.depth).all()

    samples = session.query(Sample).filter(
        Sample.linking_id == curr_link.id,
    ).order_by(Sample.depth).all()
    df = pd.DataFrame(curve, columns=['depth', 'curve'])
    print(df)

    curr_trying = session.query(Trying).filter_by(id=get_trying_id()).first()

    ui.progressBar.setMaximum(curr_trying.n_iter)
    ui.progressBar.setValue(0)

    list_skip = [i.sample_id for i in session.query(SkipSample).filter_by(trying_id=curr_trying.id).all()]

    list_val_samples = [s.value for s in samples if s.id not in list_skip]
    start_depth = [s.depth for s in samples if s.id not in list_skip]
    # list_gk = [df.loc[df['depth'] == x, 'GK'].tolist()[0] for x in start_depth]
    start_shifts = [0 for _ in start_depth]

    list_curve = [df.loc[df['depth'] == depth, 'curve'].tolist()[0] for depth in start_depth]
    old_corr, _ = pearsonr(list_curve, list_val_samples)

    def check_intersection_samples(start_depth: list, values: list, shifts: list) -> bool:
        list_samples = [[d, v] for d, v in zip(start_depth, values)]
        sort_sample = sorted(list_samples, key=lambda x: x[0])
        value_old = [i[1] for i in sort_sample]
        shift_sample = [[s[0] + shift, s[1]] for s, shift in zip(list_samples, shifts)]
        sort_shift_simple = sorted(shift_sample, key=lambda x: x[0])
        value_new, depth_new = [i[1] for i in sort_shift_simple], [i[0] for i in sort_shift_simple]

        return value_old != value_new or len(depth_new) != len(set(depth_new))


    def correlation_func(shifts, data, start_depth, list_B, param_A):
        ui.progressBar.setValue(ui.progressBar.value() + 1)
        # print("Shifts: ", shifts)
        corr_shifts = [round(i, 1) for i in shifts]
        # print("Corr_shifts: ", corr_shifts)
        if check_intersection_samples(start_depth, list_B, corr_shifts):
            return -1
        current_depth = [round(depth + x, 1) for depth, x in zip(start_depth, corr_shifts)]
        try:
            list_A = [data.loc[data['depth'] == depth, param_A].tolist()[0] for depth in current_depth]
        except IndexError:
            return -1
        corr, _ = pearsonr(list_A, list_B)

        return corr

    def shift_func(shifts):
        if curr_trying.method_shift == 'sum':
            return np.sum(np.abs(shifts))  # Минимизируем сумму абсолютных значений сдвигов
        elif curr_trying.method_shift == 'mean':
            return np.mean(np.abs(shifts))
        elif curr_trying.method_shift == 'median':
            return np.median(np.abs(shifts))

    # Определение проблемы мультиобъективной оптимизации
    problem = Problem(len(start_shifts), 2)  # Задача с len(depths_B) переменными и 2 целевыми функциями
    problem.types[:] = Real(-curr_trying.limit, curr_trying.limit)  # Ограничение на диапазон сдвигов
    problem.directions[0] = Problem.MAXIMIZE  # Минимизация отрицательной корреляции (максимизация корреляции)
    problem.directions[1] = Problem.MINIMIZE  # Минимизация суммы абсолютных значений сдвигов
    # problem.constraints[:] = ">=0"  # Ограничение на неотрицательные сдвиги
    problem.function = lambda shifts: [correlation_func(shifts, df, start_depth, list_val_samples, 'curve'), shift_func(shifts)]

    # Оптимизация с использованием NSGA-II или GDE3
    if curr_trying.algorithm == 'NSGA-II':
        algorithm = NSGAII(problem)
    else:
        algorithm = GDE3(problem)
    algorithm.run(curr_trying.n_iter)  # Запускаем алгоритм с 10000 итераций

    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(20, 16))
    ax[0, 0].scatter([s.objectives[0] for s in algorithm.result],
                  [s.objectives[1] for s in algorithm.result], marker='o', s=30, alpha=0.7)
    ax[0, 0].grid()
    ax[0, 0].set_title('Парето-фронт')

    an, bins, patches = ax[0, 1].hist([s.objectives[0] for s in algorithm.result], bins=curr_trying.bin, rwidth=0.9)

    ax[0, 1].grid()
    ax[0, 1].set_title('Гистограмма распределения значений корреляции')

    # Получение индекса последнего бина
    last_bin_idx = len(bins) - 2  # Индексы в bins от 0 до len(bins)-1, поэтому последний бин имеет индекс len(bins)-2

    # Границы последнего бина
    last_bin_min, last_bin_max = bins[last_bin_idx], bins[last_bin_idx + 1]

    # Фильтрация значений из последнего бина
    last_bin_values = [[s.objectives[0], s.objectives[1], s.variables] for s in algorithm.result if last_bin_min <= s.objectives[0] <= last_bin_max]
    try:
        best = sorted(last_bin_values, key=lambda x: x[1])[0]
    except IndexError:
        print(f"Last bin: {last_bin_values}")
        return QMessageBox.critical(MainWindow, 'Ошибка', 'Не удалось построить распределение корреляции, попробуйте увеличить количество итераций')

    best_round = [round(best[0], 3), round(best[1], 3), [round(i, 1) for i in best[2]]]
    print(f"Best solution: {best_round}")

    curr_trying.old_corr = round(old_corr, 3)
    curr_trying.corr = best_round[0]
    curr_trying.shift_value = best_round[1]

    list_samples_id = [s.id for s in samples if s.id not in list_skip]
    for n, i in enumerate(best_round[2]):
        new_shift = Shift(sample_id=list_samples_id[n], trying_id=curr_trying.id, distance=i)
        session.add(new_shift)
    session.commit()

    draw_result_linking()
    update_listwidget_trying()
    for i in range(ui.listWidget_trying.count()):
        if int(ui.listWidget_trying.item(i).text().split(' id')[-1]) == curr_trying.id:
            ui.listWidget_trying.setCurrentRow(i)
    update_listwidget_samples_for_trying()

    # fig2 = plt.figure(figsize=(25, 10))
    # ax2 = fig2.add_subplot(111)
    # ax2.plot(df['depth'], df['curve'])
    # ax2.scatter(start_depth, list_val_samples, marker='o', color='red', s=30, alpha=0.5)
    # ax2.scatter([best[2][i]+start_depth[i] for i in range(len(best[2]))], list_val_samples, marker='o', color='green', s=30, alpha=0.5)
    # ax2.grid()
    # fig2.show()

    corr_shifts = [round(i, 1) for i in best[2]]
    current_depth = [round(depth + x, 1) for depth, x in zip(start_depth, corr_shifts)]
    list_A = [df.loc[df['depth'] == depth, 'curve'].tolist()[0] for depth in current_depth]
    list_Aold = [df.loc[df['depth'] == depth, 'curve'].tolist()[0] for depth in start_depth]

    df_graph = pd.DataFrame({curr_link.param_curve: list_A,
                             curr_link.param_sample: list_val_samples,
                             f'{curr_link.param_curve} old': list_Aold})

    sns.regplot(data=df_graph, x=f'{curr_link.param_curve} old', y=curr_link.param_sample, ax=ax[1, 0])
    ax[1, 0].grid()
    ax[1, 0].set_title('График корреляции до сдвига')
    sns.regplot(data=df_graph, x=curr_link.param_curve, y=curr_link.param_sample, ax=ax[1, 1])
    ax[1, 1].grid()
    ax[1, 1].set_title('График корреляции после сдвига')
    fig.tight_layout()
    fig.show()
    plt.show()



def draw_result_linking():
    ui.graphicsView.clear()
    trying = session.query(Trying).filter_by(id=get_trying_id()).first()
    samples = session.query(Sample).filter_by(linking_id=trying.linking_id).order_by(Sample.depth).all()
    list_skip = [i.sample_id for i in session.query(SkipSample).filter_by(trying_id=trying.id).all()]
    samples = [s for s in samples if s.id not in list_skip]
    int_up, int_down = samples[0].depth, samples[-1].depth
    padding = (int_up - int_down) / 10
    tab = get_table(trying.linking.table_curve)
    curve = session.query(
        literal_column(f'{trying.linking.table_curve}.{trying.linking.param_curve}'), tab.depth
    ).filter(
        # tab.depth >= int_up + padding,
        # tab.depth <= int_down - padding,
        tab.well_id == trying.linking.well_id,
        literal_column(f'{trying.linking.table_curve}.{trying.linking.param_curve}').isnot(None)
    ).all()
    x_curve = [i[0] for i in curve]
    y_curve = [i[1] for i in curve]
    x_curve = [j / max(x_curve) for j in x_curve]
    x_sample = [i.value for i in samples]
    y_sample = [i.depth for i in samples]
    x_sample = [j / max(x_sample) for j in x_sample]

    shifts = []

    for sample in samples:
        shift = session.query(Shift).filter_by(sample_id=sample.id, trying_id=trying.id).first()
        shifts.append(shift.distance if shift else 0)
    y_sample_shift = [i + j for i, j in zip(y_sample, shifts)]

    curve_graph = pg.PlotCurveItem(x=x_curve, y=y_curve, pen=pg.mkPen(color='k', width=float(1)))
    sample_graph = pg.BarGraphItem(x0=0, y=y_sample, height=0.05, width=x_sample, brush=pg.mkBrush(color='r'),
                            pen=pg.mkPen(color='r'))
    sample_graph_shift = pg.BarGraphItem(x0=0, y=y_sample_shift, height=0.05, width=x_sample, brush=pg.mkBrush(color='green'),
                            pen=pg.mkPen(color='green'))

    ui.graphicsView.addItem(curve_graph)
    curve_graph.getViewBox().invertY(True)
    ui.graphicsView.addItem(sample_graph)
    sample_graph.getViewBox().invertY(True)
    ui.graphicsView.addItem(sample_graph_shift)
    sample_graph_shift.getViewBox().invertY(True)
    ui.graphicsView.setYRange(int_up, int_down, padding=-padding)



def draw_result_linking_sample():
    draw_result_linking()
    sample = session.query(Sample).filter_by(id=get_sample_id()).first()
    shift = session.query(Shift).filter_by(sample_id=sample.id, trying_id=get_trying_id()).first()

    depth_line1 = pg.InfiniteLine(angle=0, pen=pg.mkPen(color='b', width=1, dash=[2, 2]))
    ui.graphicsView.addItem(depth_line1)
    depth_line1.setPos(sample.depth)
    if shift:
        depth_line2 = pg.InfiniteLine(angle=0, pen=pg.mkPen(color='b', width=1, dash=[2, 2]))
        ui.graphicsView.addItem(depth_line2)
        depth_line2.setPos(sample.depth + shift.distance)


def remove_trying():
    trying = session.query(Trying).filter_by(id=get_trying_id()).first()
    for i in trying.shifts:
        session.delete(i)
    for i in trying.skips:
        session.delete(i)
    session.delete(trying)
    session.commit()
    update_listwidget_trying()


def set_linking_options():
    trying = session.query(Trying).filter_by(id=get_trying_id()).first()
    ui.comboBox_opt_algorithm.setCurrentText(trying.algorithm)
    ui.comboBox_shift_method.setCurrentText(trying.method_shift)
    ui.spinBox_n_iter_linking.setValue(trying.n_iter)
    ui.spinBox_linking_bin.setValue(trying.bin)
    ui.doubleSpinBox_lim_shift.setValue(trying.limit)


