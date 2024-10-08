from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_NAME = 'domanic_db.sqlite'

engine = create_engine(f'sqlite:///{DATABASE_NAME}', echo=False)
Session = sessionmaker(bind=engine)

Base = declarative_base()


class Region(Base):
    __tablename__ = 'regions'

    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True)


class Area(Base):
    __tablename__ = 'areas'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=False)

    region = relationship("Region", backref="areas")


class Well(Base):
    __tablename__ = 'wells'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    area_id = Column(Integer, ForeignKey('areas.id'), nullable=False)

    area = relationship("Area", backref='wells')
    user_interval = relationship("UserInterval", back_populates='well')
    compare_interval = relationship("CompareInterval", back_populates='well')
    regression_analysis = relationship("RegressionWell", back_populates='well')
    linkings = relationship("Linking", back_populates='well')
    used_shifts = relationship("UsedShift", back_populates='well')


class DataAge(Base):
    __tablename__ = 'data_age'

    id = Column(Integer, primary_key=True)
    depth = Column(Float)
    age = Column(String)
    well_id = Column(Integer, ForeignKey('wells.id'), nullable=False)

    well = relationship("Well", backref='data_age')


class DataPirolizKern(Base):
    __tablename__ = 'data_piroliz_kern'

    id = Column(Integer, primary_key=True)
    depth = Column(Float)
    name = Column(String)
    well_id = Column(Integer, ForeignKey('wells.id'), nullable=False)

    well = relationship("Well", backref='data_piroliz_kern')

    s1 = Column(Float)
    s2 = Column(Float)
    s3 = Column(Float)
    s3_ = Column(Float)
    s3co = Column(Float)
    s3_co = Column(Float)
    s4co2 = Column(Float)
    s5 = Column(Float)
    s4co = Column(Float)
    tmax = Column(Float)

    pc = Column(Float)
    rc = Column(Float)
    toc = Column(Float)
    pp = Column(Float)
    cmin = Column(Float)
    nop = Column(Float)
    hi = Column(Float)
    s1_toc = Column(Float)
    oxminc = Column(Float)
    prminc = Column(Float)
    pi = Column(Float)
    oi = Column(Float)
    oico = Column(Float)

    s1r_r = Column(Float)
    s2a_r = Column(Float)
    oil_r = Column(Float)
    s2b_r = Column(Float)
    tmax_r = Column(Float)
    s3_r = Column(Float)
    pc_r = Column(Float)
    rc_r = Column(Float)
    toc_r = Column(Float)
    cmin_r = Column(Float)
    hi_r = Column(Float)
    oi_r = Column(Float)
    tpi_r = Column(Float)
    nso_kero_r = Column(Float)
    light_oil_r = Column(Float)
    heavy_oil_r = Column(Float)
    nso_kero_part_r = Column(Float)
    osi_r = Column(Float)
    api_index = Column(Float)


class DataPirolizExtr(Base):
    __tablename__ = 'data_piroliz_extr'

    id = Column(Integer, primary_key=True)
    depth = Column(Float)
    name = Column(String)
    well_id = Column(Integer, ForeignKey('wells.id'), nullable=False)

    well = relationship("Well", backref='data_piroliz_extr')

    s1 = Column(Float)
    s2 = Column(Float)
    s3 = Column(Float)
    s3_ = Column(Float)
    s3co = Column(Float)
    s3_co = Column(Float)
    s4co2 = Column(Float)
    s5 = Column(Float)
    s4co = Column(Float)
    tmax = Column(Float)

    pc = Column(Float)
    rc = Column(Float)
    toc = Column(Float)
    pp = Column(Float)
    cmin = Column(Float)
    hi = Column(Float)
    s1_toc = Column(Float)
    oxminc = Column(Float)
    prminc = Column(Float)
    pi = Column(Float)
    oi = Column(Float)
    oico = Column(Float)

    s1r_r = Column(Float)
    s2a_r = Column(Float)
    oil_r = Column(Float)
    s2b_r = Column(Float)
    tmax_r = Column(Float)
    s3_r = Column(Float)
    pc_r = Column(Float)
    rc_r = Column(Float)
    toc_r = Column(Float)
    cmin_r = Column(Float)
    hi_r = Column(Float)
    oi_r = Column(Float)
    tpi_r = Column(Float)
    nso_kero_r = Column(Float)
    light_oil_r = Column(Float)
    heavy_oil_r = Column(Float)
    nso_kero_part_r = Column(Float)
    osi_r = Column(Float)
    api_index = Column(Float)


class DataChromExtr(Base):
    __tablename__ = 'data_chrom_extr'

    id = Column(Integer, primary_key=True)
    depth = Column(Float)
    name = Column(String)
    well_id = Column(Integer, ForeignKey('wells.id'), nullable=False)

    well = relationship("Well", backref='data_chrom_extr')

    Heptane_C7 = Column(Float)
    Octane_C8 = Column(Float)
    Nonane_C9 = Column(Float)
    Decane_C10 = Column(Float)
    Undecane_C11 = Column(Float)
    Dodecane_C12 = Column(Float)
    Tridecane_C13 = Column(Float)
    Tetradecane_C14 = Column(Float)
    Pentadecane_C15 = Column(Float)
    Hexadecane_C16 = Column(Float)
    Heptadecane_C17 = Column(Float)
    Pristane = Column(Float)
    Octadecane_C18 = Column(Float)
    Phytane = Column(Float)
    Nonadecane_C19 = Column(Float)
    Eicosane_C20 = Column(Float)
    Heneicosane_C21 = Column(Float)
    Docosane_C22 = Column(Float)
    Tricosane_C23 = Column(Float)
    Tetracosane_C24 = Column(Float)
    Pentacosane_C25 = Column(Float)
    Hexacosane_C26 = Column(Float)
    Heptacosane_C27 = Column(Float)
    Octacosane_C28 = Column(Float)
    Nonacosane_C29 = Column(Float)
    Triacontane_C30 = Column(Float)
    Hentriacontane_C31 = Column(Float)
    Dotriacontane_C32 = Column(Float)
    Tritriacontane_C33 = Column(Float)
    Tetratriacontane_C34 = Column(Float)
    Pentatriacontane_C35 = Column(Float)
    Hexatriacontane_C36 = Column(Float)
    Heptatriacontane_C37 = Column(Float)
    Octatriacontane_C38 = Column(Float)
    Nonatriacontane_C39 = Column(Float)
    Tetracontane_C40 = Column(Float)

    Pr__Ph = Column(Float)
    Pr__n_C17 = Column(Float)
    Ph__n_C18 = Column(Float)
    Ki = Column(Float)
    C27__C17 = Column(Float)
    CPI_nC19_nC23 = Column(Float)
    CPI_nC17_nC21 = Column(Float)
    CPI_nC19_nC25 = Column(Float)
    CPI_nC23_nC29 = Column(Float)
    CPI_nC23_nC33 = Column(Float)
    OEP_nC19 = Column(Float)
    OEP_nC21 = Column(Float)
    OEP_nC23 = Column(Float)
    OEP_nC25 = Column(Float)
    OEP_nC27 = Column(Float)
    OEP_nC29 = Column(Float)
    CPI_nC25_nC33 = Column(Float)
    nC17__nC25 = Column(Float)
    nC16_nC22__nC23_nC29 = Column(Float)
    nC35__nC34 = Column(Float)
    nC15_nC20 = Column(Float)
    nC21_nC30 = Column(Float)
    nC15_nC20__nC21_nC30 = Column(Float)
    nC16_nC22 = Column(Float)
    nC23_nC29 = Column(Float)
    nC15_nC17__nC22_nC24 = Column(Float)
    nC25_nC33__nC26_nC34 = Column(Float)
    nC11_nC18 = Column(Float)
    nC15_nC19__nC25_nC29 = Column(Float)


class DataChromKern(Base):
    __tablename__ = 'data_chrom_kern'

    id = Column(Integer, primary_key=True)
    depth = Column(Float)
    name = Column(String)
    well_id = Column(Integer, ForeignKey('wells.id'), nullable=False)

    well = relationship("Well", backref='data_chrom_kern')

    Heptane_C7 = Column(Float)
    Octane_C8 = Column(Float)
    Nonane_C9 = Column(Float)
    Decane_C10 = Column(Float)
    Undecane_C11 = Column(Float)
    Dodecane_C12 = Column(Float)
    Tridecane_C13 = Column(Float)
    Tetradecane_C14 = Column(Float)
    Pentadecane_C15 = Column(Float)
    Hexadecane_C16 = Column(Float)
    Heptadecane_C17 = Column(Float)
    Pristane = Column(Float)
    Octadecane_C18 = Column(Float)
    Phytane = Column(Float)
    Nonadecane_C19 = Column(Float)
    Eicosane_C20 = Column(Float)
    Heneicosane_C21 = Column(Float)
    Docosane_C22 = Column(Float)
    Tricosane_C23 = Column(Float)
    Tetracosane_C24 = Column(Float)
    Pentacosane_C25 = Column(Float)
    Hexacosane_C26 = Column(Float)
    Heptacosane_C27 = Column(Float)
    Octacosane_C28 = Column(Float)
    Nonacosane_C29 = Column(Float)
    Triacontane_C30 = Column(Float)
    Hentriacontane_C31 = Column(Float)
    Dotriacontane_C32 = Column(Float)
    Tritriacontane_C33 = Column(Float)
    Tetratriacontane_C34 = Column(Float)
    Pentatriacontane_C35 = Column(Float)
    Hexatriacontane_C36 = Column(Float)
    Heptatriacontane_C37 = Column(Float)
    Octatriacontane_C38 = Column(Float)
    Nonatriacontane_C39 = Column(Float)
    Tetracontane_C40 = Column(Float)

    Pr__Ph = Column(Float)
    Pr__n_C17 = Column(Float)
    Ph__n_C18 = Column(Float)
    Ki = Column(Float)
    C27__C17 = Column(Float)
    CPI_nC19_nC23 = Column(Float)
    CPI_nC17_nC21 = Column(Float)
    CPI_nC19_nC25 = Column(Float)
    CPI_nC23_nC29 = Column(Float)
    CPI_nC23_nC33 = Column(Float)
    OEP_nC19 = Column(Float)
    OEP_nC21 = Column(Float)
    OEP_nC23 = Column(Float)
    OEP_nC25 = Column(Float)
    OEP_nC27 = Column(Float)
    OEP_nC29 = Column(Float)
    CPI_nC25_nC33 = Column(Float)
    nC17__nC25 = Column(Float)
    nC16_nC22__nC23_nC29 = Column(Float)
    nC35__nC34 = Column(Float)
    nC15_nC20 = Column(Float)
    nC21_nC30 = Column(Float)
    nC15_nC20__nC21_nC30 = Column(Float)
    nC16_nC22 = Column(Float)
    nC23_nC29 = Column(Float)
    nC15_nC17__nC22_nC24 = Column(Float)
    nC25_nC33__nC26_nC34 = Column(Float)
    nC11_nC18 = Column(Float)
    nC15_nC19__nC25_nC29 = Column(Float)


class DataLas(Base):
    __tablename__ = 'data_las'

    id = Column(Integer, primary_key=True)
    depth = Column(Float)
    well_id = Column(Integer, ForeignKey('wells.id'), nullable=False)

    well = relationship("Well", backref='data_las')

    DS = Column(Float)
    DS1 = Column(Float)
    DS2 = Column(Float)
    PZ = Column(Float)
    SP = Column(Float)
    RS = Column(Float)
    GK = Column(Float)
    GGK = Column(Float)
    RIK = Column(Float)
    BK = Column(Float)
    NKTS = Column(Float)
    NKTD = Column(Float)
    WNK = Column(Float)
    POTA = Column(Float)
    THOR = Column(Float)
    URAN = Column(Float)
    INTEGRAL = Column(Float)
    UEKT = Column(Float)
    NML1 = Column(Float)
    NML2 = Column(Float)
    NML3 = Column(Float)
    DTP = Column(Float)
    T1 = Column(Float)
    T2 = Column(Float)
    Mgl = Column(Float)
    IK = Column(Float)
    W = Column(Float)
    NNKb = Column(Float)
    NNKm = Column(Float)
    NGK = Column(Float)

    Rp = Column(Float)
    PROD= Column(Float)
    PHIg = Column(Float)
    LITOc = Column(Float)
    KPR_A = Column(Float)
    KPGKS = Column(Float)
    Kgl = Column(Float)
    FLUIDc = Column(Float)
    COLLc = Column(Float)
    Ang = Column(Float)
    Ag = Column(Float)

    SUM_GAS = Column(Float)

    GZ1 = Column(Float)
    GZ2 = Column(Float)
    GZ3 = Column(Float)
    GZ4 = Column(Float)
    GZ5 = Column(Float)
    GZR = Column(Float)


class DataLit(Base):
    __tablename__ = 'data_lit'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    depth = Column(Float)
    well_id = Column(Integer, ForeignKey('wells.id'), nullable=False)

    well = relationship("Well", backref='data_lit')

    porosity = Column(Float)
    permeability = Column(Float)
    density = Column(Float)
    oil_saturation = Column(Float)
    carbonate_content = Column(Float)
    silicicity = Column(Float)
    lithotype = Column(Float)

    calcite = Column(Float)
    silica = Column(Float)
    orthoclase = Column(Float)
    muscovite = Column(Float)
    marcasite = Column(Float)
    ankerite = Column(Float)
    illite = Column(Float)
    albite = Column(Float)
    dolomite = Column(Float)
    pyrite = Column(Float)
    siderite = Column(Float)
    halite = Column(Float)
    biotite = Column(Float)
    kaolinite = Column(Float)
    quartz = Column(Float)

    k40_bk = Column(Float)
    k40_U = Column(Float)
    k40_percent = Column(Float)
    ra226_bk = Column(Float)
    ra226_U = Column(Float)
    ra226_ppm = Column(Float)
    th232_bk = Column(Float)
    th232_U = Column(Float)
    th232_ppm = Column(Float)
    Asum_ppm = Column(Float)
    Asum_bk = Column(Float)
    Aef_bk = Column(Float)
    SGK = Column(Float)


class DrawSeveralGraph(Base):
    __tablename__ = 'draw_several_graph'

    id = Column(Integer, primary_key=True)
    well_id = Column(Integer, ForeignKey('wells.id'), nullable=False)

    well = relationship("Well", backref='draw_several_graph')

    table = Column(String)
    param = Column(String)
    color = Column(String)
    dash = Column(String)
    width = Column(String)


class DrawGraphTablet(Base):
    __tablename__ = 'draw_graph_tablet'

    id = Column(Integer, primary_key=True)
    well_id = Column(Integer, ForeignKey('wells.id'), nullable=False)

    well = relationship("Well", backref='draw_graph_tablet')

    table = Column(String)
    param = Column(String)
    color = Column(String)
    dash = Column(String)
    width = Column(String)
    type_graph = Column(String)


class TemplateGraphTablet(Base):
    __tablename__ = 'template_graph_tablet'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    table = Column(String)
    param = Column(String)
    color = Column(String)
    dash = Column(String)
    width = Column(String)
    type_graph = Column(String)


class ClassByLimits(Base):
    __tablename__ = 'class_by_limits'

    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True)
    category_names = Column(String)

    params = relationship('ClassByLimitsParam', back_populates='classificate', cascade="all, delete-orphan", passive_deletes=True)


class ClassByLimitsParam(Base):
    __tablename__ = 'class_by_limits_param'

    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey('class_by_limits.id', ondelete='CASCADE'))

    classificate = relationship('ClassByLimits', back_populates='params', passive_deletes=True)

    table = Column(String)
    param = Column(String)
    limits = Column(String)


class ClassByLda(Base):
    __tablename__ = 'class_by_LDA'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    well_id = Column(Integer, ForeignKey('wells.id'), nullable=False)
    category = Column(String)

    well = relationship('Well', backref='class_by_LDA')


class ClassByLdaMark(Base):
    __tablename__ = 'class_by_LDA_mark'

    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey('class_by_LDA.id', ondelete='CASCADE'))
    depth = Column(Float)
    mark = Column(String)
    fake = Column(Boolean, default=False)

    class_lda = relationship('ClassByLda', backref='class_by_LDA_mark')


class IntervalFromCat(Base):
    __tablename__ = 'interval_from_cat'

    id = Column(Integer, primary_key=True)
    int_from = Column(Float)
    int_to = Column(Float)


class UserInterval(Base):
    __tablename__ = 'user_interval'

    id = Column(Integer, primary_key=True)
    well_id = Column(Integer, ForeignKey('wells.id'), nullable=False)
    int_from = Column(Float)
    int_to = Column(Float)
    title = Column(String)
    color = Column(String)

    well = relationship("Well", back_populates='user_interval')


class CompareInterval(Base):
    __tablename__ = 'compare_interval'

    id = Column(Integer, primary_key=True)
    well_id = Column(Integer, ForeignKey('wells.id'), nullable=False)
    int_from = Column(Float)
    int_to = Column(Float)
    title = Column(String)
    color = Column(String)

    well = relationship("Well", back_populates='compare_interval')


###########################################################################
############################### Regression ################################
###########################################################################


class RegressionAnalysis(Base):
    __tablename__ = 'regression_analysis'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    target_param = Column(String)

    regression_features = relationship('RegressionFeature', back_populates='regression_analysis')
    wells = relationship('RegressionWell', back_populates='regression_analysis')


class RegressionFeature(Base):
    __tablename__ = 'regression_feature'

    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey('regression_analysis.id'))
    table_features = Column(String)
    param_features = Column(String)

    regression_analysis = relationship('RegressionAnalysis', back_populates='regression_features')


class RegressionWell(Base):
    __tablename__ = 'regression_well'

    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey('regression_analysis.id'))
    well_id = Column(Integer, ForeignKey('wells.id'))
    int_from = Column(Float)
    int_to = Column(Float)

    regression_analysis = relationship('RegressionAnalysis', back_populates='wells')
    well = relationship('Well', back_populates='regression_analysis')


class TrainedRegModel(Base):
    __tablename__ = 'trained_reg_model'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    path_model = Column(String)
    path_scaler = Column(String)
    target_param = Column(String)
    list_params = Column(Text)
    list_wells = Column(Text)
    comment = Column(Text)


class CalculatedData(Base):
    __tablename__ = 'calculated_data'

    id = Column(Integer, primary_key=True)
    well_id = Column(Integer, ForeignKey('wells.id'), nullable=False)
    title = Column(String)
    data = Column(Text)
    model_title = Column(String)
    list_params_model = Column(Text)
    list_wells_model = Column(Text)
    comment = Column(Text)


########################
####### LINKING ########
########################

class Linking(Base):
    __tablename__ = 'linking'

    id = Column(Integer, primary_key=True)
    well_id = Column(Integer, ForeignKey('wells.id'), nullable=False)
    table_curve = Column(String)
    param_curve = Column(String)
    table_sample = Column(String)
    param_sample = Column(String)

    well = relationship('Well', back_populates='linkings')
    samples = relationship('Sample', back_populates='linking')
    tryings = relationship('Trying', back_populates='linking')


class Sample(Base):
    __tablename__ = 'sample'

    id = Column(Integer, primary_key=True)
    linking_id = Column(Integer, ForeignKey('linking.id'))
    value = Column(Float)
    depth = Column(Float)

    linking = relationship('Linking', back_populates='samples')
    shifts = relationship('Shift', back_populates='sample')
    skips = relationship('SkipSample', back_populates='sample')


class Trying(Base):
    __tablename__ = 'trying'

    id = Column(Integer, primary_key=True)
    linking_id = Column(Integer, ForeignKey('linking.id'))
    up_depth = Column(Float)
    down_depth = Column(Float)
    algorithm = Column(String)
    method_shift = Column(String)
    n_iter = Column(Integer)
    limit = Column(Float)
    bin = Column(Integer)
    old_corr = Column(Float)
    corr = Column(Float)
    shift_value = Column(Float)
    used = Column(Boolean, default=False)

    linking = relationship('Linking', back_populates='tryings')
    shifts = relationship('Shift', back_populates='trying')
    skips = relationship('SkipSample', back_populates='trying')


class SkipSample(Base):
    __tablename__ = 'skip_sample'

    id = Column(Integer, primary_key=True)
    trying_id = Column(Integer, ForeignKey('trying.id'))
    sample_id = Column(Integer, ForeignKey('sample.id'))

    trying = relationship('Trying', back_populates='skips')
    sample = relationship('Sample', back_populates='skips')

class Shift(Base):
    __tablename__ = 'shift'

    id = Column(Integer, primary_key=True)
    trying_id = Column(Integer, ForeignKey('trying.id'))
    sample_id = Column(Integer, ForeignKey('sample.id'))
    distance = Column(Float)

    trying = relationship('Trying', back_populates='shifts')
    sample = relationship('Sample', back_populates='shifts')
    used_shift = relationship('UsedShift', back_populates='shift')


class UsedShift(Base):
    __tablename__ = 'used_shift'

    id = Column(Integer, primary_key=True)
    shift_id = Column(Integer, ForeignKey('shift.id'))
    well_id = Column(Integer, ForeignKey('wells.id'))
    table_name = Column(String)
    tab_sample_id = Column(Integer)
    start_depth = Column(Float)

    shift = relationship('Shift', back_populates='used_shift')
    well = relationship('Well', back_populates='used_shifts')


Base.metadata.create_all(engine)
