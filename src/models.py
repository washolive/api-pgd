"""Definições dos modelos de dados da API que serão persistidos no
banco pelo ORM do SQLAlchemy.
"""

from sqlalchemy import (Boolean, Column, ForeignKey,
                        Integer, BigInteger,String, Float, Date, DateTime,
                        UniqueConstraint)
from sqlalchemy import event, DDL
from sqlalchemy.orm import relationship

from users import Base

class PlanoTrabalho(Base):
    "Plano de Trabalho"
    __tablename__ = "plano_trabalho"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    situacao = Column(String)
    cod_unidade = Column(BigInteger, nullable=False)
    cod_plano = Column(String, nullable=False)
    matricula_siape = Column(Integer)
    cpf = Column(String)
    nome_participante = Column(String)
    cod_unidade_exercicio = Column(BigInteger)
    nome_unidade_exercicio = Column(String)
    modalidade_execucao = Column(Integer)
    carga_horaria_semanal = Column(Integer)
    data_inicio = Column(Date)
    data_fim = Column(Date)
    carga_horaria_total = Column(Float)
    data_interrupcao = Column(Date)
    entregue_no_prazo = Column(Boolean) #TODO Na especificação está como Int e usa 1 e 2 para sim e não. Não seria melhor usar bool?
    horas_homologadas = Column(Float)
    data_atualizacao = Column(DateTime)
    data_insercao = Column(DateTime)
    atividades = relationship(
        "Atividade",
        back_populates="plano_trabalho",
        lazy="joined",
        passive_deletes=True,
        cascade="save-update, merge, delete, delete-orphan"
    )
    __table_args__ = (UniqueConstraint(
        "cod_unidade",
        "cod_plano",
        name="_unidade_plano_uc"
    ),)

# trigger = DDL("""
#     CREATE TRIGGER inseredata_trigger
#     BEFORE INSERT OR UPDATE ON public.plano_trabalho
#     FOR EACH ROW EXECUTE PROCEDURE insere_data_registro();
# """
# )

# event.listen(
#     PlanoTrabalho.__table__,
#     'after_create',
#     trigger.execute_if(dialect='postgresql')
# )

# trigger = DDL("""
#     CREATE TRIGGER inseredata_trigger
#     BEFORE INSERT OR UPDATE ON public.atividade
#     FOR EACH ROW EXECUTE PROCEDURE insere_data_registro();
# """
# )

# event.listen(
#     Atividade.__table__,
#     'after_create',
#     trigger.execute_if(dialect='postgresql')
# )
