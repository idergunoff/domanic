from functions import *


def add_regression_analysis():
    """ Добавление регрессионного анализа """
    title_text = ui.lineEdit_string.text()
    if title_text != '':
        new_reg_analysis = RegressionAnalysis(title=title_text, target_param='data_piroliz_kern.toc')
        session.add(new_reg_analysis)
        session.commit()
        set_label_info(f'Добавлен новый регрессионный анализ "{title_text}"', 'green')
        update_list_regression_analysis()
    else:
        set_label_info('Введите название модели в текстовое поле в верхней правой части главного окна.', 'red')
        QMessageBox.critical(MainWindow, 'Ошибка!', 'Введите название модели в текстовое поле в верхней правой части главного окна.')



def remove_regression_analysis():
    """ Удаление регрессионного анализа """
    an = session.query(RegressionAnalysis).filter_by(id=ui.comboBox_reg_analysis.currentText().split(' id')[-1]).first()
    an_title = an.title
    session.delete(an)
    session.commit()
    update_list_regression_analysis()
    set_label_info(f'Регрессионный анализ "{an_title}" удалён.', 'green')


def update_list_regression_analysis():
    """ Обновление списка регрессионного анализа """
    ui.comboBox_reg_analysis.clear()
    for an in session.query(RegressionAnalysis).all():
        ui.comboBox_reg_analysis.addItem(f'{an.title} id{an.id}')
    set_target_param()


def set_target_param():
    """ Установка параметра целевой переменной """
    if ui.comboBox_reg_analysis.currentText():
        an = session.query(RegressionAnalysis).filter_by(id=ui.comboBox_reg_analysis.currentText().split(' id')[-1]).first()
        ui.label_target_table.setText(an.target_param.split('.')[0])
        ui.label_target_param.setText(an.target_param.split('.')[1])


def update_new_target_param():
    """ Обновление параметра целевой переменной """
    table, table_text, widget = check_tabWidjet()
    session.query(RegressionAnalysis).filter_by(id=ui.comboBox_reg_analysis.currentText().split(' id')[-1]).update(
        {'target_param': f'{table_text}.{widget.currentItem().text()}'},
        synchronize_session='fetch'
    )
    session.commit()
    set_label_info('Параметр целевой переменной обновлен.', 'green')
    set_target_param()


def add_regression_well():
    """ Добавление скважины в регрессионный анализ """
    pass


def remove_regression_well():
    """ Удаление скважины из регрессионного анализа """
    pass


def update_list_regression_well():
    """ Обновление списка скважин в регрессионном анализе """
    set_target_param()


def update_list_features_regression():
    """ Обновление списка признаков в регрессионном анализе """
    pass


def add_feature_regression():
    """ Добавление признака в регрессионный анализ """
    pass


def remove_feature_regression():
    """ Удаление признака из регрессионного анализа """
    pass


def add_all_table_to_features_regression():
    """ Добавление всей таблицы в признаки регрессионного анализа """
    pass


def clear_list_features_regression():
    """ Очистка списка признаков в регрессионном анализе """
    pass


def train_regression_model():
    """ Обучение модели регрессионного анализа """
    pass


def remove_trained_regression_model():
    """ Удаление обученной модели регрессионного анализа """
    pass


def calc_regression_model():
    """ Расчёт модели регрессионного анализа """
    pass