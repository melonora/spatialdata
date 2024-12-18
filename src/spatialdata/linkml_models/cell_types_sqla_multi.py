
from sqlalchemy import Column, Index, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()
metadata = Base.metadata


class CellTypeAnnotationSummary(Base):
    """
    Represents the summarized information extracted from a table.
    """
    __tablename__ = 'CellTypeAnnotationSummary'

    table_col_id = Column(Text(), primary_key=True, nullable=False )
    
    
    # ManyToMany
    cell_type_statistics = relationship( "CellTypeStatistics", secondary="CellTypeAnnotationSummary_cell_type_statistics")
    

    def __repr__(self):
        return f"CellTypeAnnotationSummary(table_col_id={self.table_col_id},)"



    


class CellTypeStatistics(Base):
    """
    Summary statistics for a specific cell type.
    """
    __tablename__ = 'CellTypeStatistics'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    total_cells = Column(Integer(), nullable=False )
    relative_abundance = Column(Float())
    cell_type_information_id = Column(Integer(), ForeignKey('CellType.id'), nullable=False )
    cell_type_information = relationship("CellType", uselist=False, foreign_keys=[cell_type_information_id])
    
    
    # ManyToMany
    marker_statistics = relationship( "MarkerStatistics", secondary="CellTypeStatistics_marker_statistics")
    

    def __repr__(self):
        return f"CellTypeStatistics(id={self.id},total_cells={self.total_cells},relative_abundance={self.relative_abundance},cell_type_information_id={self.cell_type_information_id},)"



    


class CellType(Base):
    """
    A cell type is a distinct morphological or functional form of cell. Examples are epithelial, glial etc.
    """
    __tablename__ = 'CellType'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    cell_type_name = Column(Text())
    
    
    marker_set_rel = relationship( "CellTypeMarkerSet" )
    marker_set = association_proxy("marker_set_rel", "marker_set",
                                  creator=lambda x_: CellTypeMarkerSet(marker_set=x_))
    

    def __repr__(self):
        return f"CellType(id={self.id},cell_type_name={self.cell_type_name},)"



    


class MarkerStatistics(Base):
    """
    Represents marker-based statistics for a cell type.
    """
    __tablename__ = 'MarkerStatistics'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    marker_name = Column(Text())
    inclusive_mean_expression = Column(Float())
    exclusive_mean_expression = Column(Float())
    inclusive_expression_range_id = Column(Integer(), ForeignKey('ExpressionRange.id'))
    inclusive_expression_range = relationship("ExpressionRange", uselist=False, foreign_keys=[inclusive_expression_range_id])
    exclusive_expression_range_id = Column(Integer(), ForeignKey('ExpressionRange.id'))
    exclusive_expression_range = relationship("ExpressionRange", uselist=False, foreign_keys=[exclusive_expression_range_id])
    

    def __repr__(self):
        return f"MarkerStatistics(id={self.id},marker_name={self.marker_name},inclusive_mean_expression={self.inclusive_mean_expression},exclusive_mean_expression={self.exclusive_mean_expression},inclusive_expression_range_id={self.inclusive_expression_range_id},exclusive_expression_range_id={self.exclusive_expression_range_id},)"



    


class ExpressionRange(Base):
    """
    Represents the range of expression values for a marker.
    """
    __tablename__ = 'ExpressionRange'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    min_expression = Column(Float())
    max_expression = Column(Float())
    

    def __repr__(self):
        return f"ExpressionRange(id={self.id},min_expression={self.min_expression},max_expression={self.max_expression},)"



    


class CellTypeAnnotationSummaryCellTypeStatistics(Base):
    """
    
    """
    __tablename__ = 'CellTypeAnnotationSummary_cell_type_statistics'

    CellTypeAnnotationSummary_table_col_id = Column(Text(), ForeignKey('CellTypeAnnotationSummary.table_col_id'), primary_key=True)
    cell_type_statistics_id = Column(Integer(), ForeignKey('CellTypeStatistics.id'), primary_key=True, nullable=False )
    

    def __repr__(self):
        return f"CellTypeAnnotationSummary_cell_type_statistics(CellTypeAnnotationSummary_table_col_id={self.CellTypeAnnotationSummary_table_col_id},cell_type_statistics_id={self.cell_type_statistics_id},)"



    


class CellTypeStatisticsMarkerStatistics(Base):
    """
    
    """
    __tablename__ = 'CellTypeStatistics_marker_statistics'

    CellTypeStatistics_id = Column(Integer(), ForeignKey('CellTypeStatistics.id'), primary_key=True)
    marker_statistics_id = Column(Integer(), ForeignKey('MarkerStatistics.id'), primary_key=True)
    

    def __repr__(self):
        return f"CellTypeStatistics_marker_statistics(CellTypeStatistics_id={self.CellTypeStatistics_id},marker_statistics_id={self.marker_statistics_id},)"



    


class CellTypeMarkerSet(Base):
    """
    
    """
    __tablename__ = 'CellType_marker_set'

    CellType_id = Column(Integer(), ForeignKey('CellType.id'), primary_key=True)
    marker_set = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"CellType_marker_set(CellType_id={self.CellType_id},marker_set={self.marker_set},)"



    


