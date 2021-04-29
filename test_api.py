"""
Testes automáticos da API
"""
import os, subprocess
import json
from typing import Callable, Generator, Optional
from requests.models import Response as HTTPResponse
import requests

from fastapi.testclient import TestClient
from requests import Session
from fastapi import status
from api import app
import pytest

# Helper functions

def register_user(
        client: Session,
        email: str,
        password: str,
        cod_unidade: int,
        headers: dict
    ) -> HTTPResponse:
    data = {
        "email": email,
        "password": password,
        "cod_unidade": cod_unidade,
    }
    return client.post(
        f"/auth/register",
        json=data,
        headers=headers
    )

def prepare_header(username: Optional[str], password: Optional[str]) -> dict:
    token_user = None

    if username and password:
        # usuário especificado, é necessário fazer login
        url = "http://localhost:5057/auth/jwt/login"

        headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }

        payload='&'.join([
            'accept=application%2Fjson',
            'Content-Type=application%2Fjson',
            f'username={username}',
            f'password={password}'
        ])

        response = requests.request("POST", url, headers=headers, data=payload)
        response_dict = json.loads(response.text)
        token_user = response_dict.get('access_token')
        print(token_user)

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    if token_user:
        headers['Authorization'] = f'Bearer {token_user}'
    
    return headers


# Fixtures

@pytest.fixture(scope="module")
def client() -> Generator[Session, None, None]:
    with TestClient(app) as c:
        yield c

@pytest.fixture()
def input_pt() -> dict:
    pt_json = {
  "cod_plano": "555",
  "matricula_siape": 0,
  "cpf": "99160773120",
  "nome_participante": "string",
  "cod_unidade_exercicio": 0,
  "nome_unidade_exercicio": "string",
  "modalidade_execucao": 1,
  "carga_horaria_semanal": 10,
  "data_inicio": "2021-01-07",
  "data_fim": "2021-01-12",
  "carga_horaria_total": 0,
  "data_interrupcao": "2021-01-07",
  "entregue_no_prazo": True,
  "horas_homologadas": 0,
  "atividades": [
    {
      "id_atividade": 2,
      "nome_grupo_atividade": "string",
      "nome_atividade": "string",
      "faixa_complexidade": "string",
      "parametros_complexidade": "string",
      "tempo_exec_presencial": 0,
      "tempo_exec_teletrabalho": 0,
      "entrega_esperada": "string",
      "qtde_entregas": 0,
      "qtde_entregas_efetivas": 0,
      "avaliacao": 0,
      "data_avaliacao": "2021-01-15",
      "justificativa": "string"
    },
    {
      "id_atividade": 3,
      "nome_grupo_atividade": "string",
      "nome_atividade": "string",
      "faixa_complexidade": "string",
      "parametros_complexidade": "string",
      "tempo_exec_presencial": 0,
      "tempo_exec_teletrabalho": 0,
      "entrega_esperada": "string",
      "qtde_entregas": 0,
      "qtde_entregas_efetivas": 0,
      "avaliacao": 0,
      "data_avaliacao": "2021-01-15",
      "justificativa": "string"
    }
  ]
}
    return pt_json

@pytest.fixture(scope="module")
def admin_credentials() -> dict:
    return {
        'username': 'admin@api.com',
        'password': '1234',
        'cod_unidade': 1
    }

@pytest.fixture(scope="module")
def user1_credentials() -> dict:
    return {
        'username': 'test1@api.com',
        'password': 'api',
        'cod_unidade': 1
    }

@pytest.fixture(scope="module")
def user2_credentials() -> dict:
    return {
        'username': 'test2@api.com',
        'password': 'api',
        'cod_unidade': 2
    }

@pytest.fixture()
def example_pt(client: Session, input_pt: dict, header_usr_1: dict):
    client.put(f"/plano_trabalho/555",
                          json=input_pt,
                          headers=header_usr_1)

@pytest.fixture(scope="module")
def truncate_pt(client: Session, header_admin: dict):
    client.post(f"/truncate_pts_atividades", headers=header_admin)

@pytest.fixture(scope="module")
def truncate_users():
    p = subprocess.Popen(
        [
            '/usr/local/bin/python',
            '/home/api-pgd/admin_tool.py',
            '--truncate-users'
        ],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

@pytest.fixture(scope="module")
def register_admin(truncate_users, admin_credentials: dict):
    email = admin_credentials['username']
    cod_unidade = admin_credentials['cod_unidade']
    password = admin_credentials['password']
    p = subprocess.Popen(
        [
            '/usr/local/bin/python',
            '/home/api-pgd/admin_tool.py',
            '--create_superuser'
        ],
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    p.communicate(input='\n'.join([
        email, str(cod_unidade), password, password
    ]))[0]

@pytest.fixture(scope="module")
def register_user_1(
    client: Session,
    truncate_users,
    register_admin,
    header_admin: dict,
    user1_credentials: dict
    ) -> HTTPResponse:
    return register_user(client, user1_credentials['username'],
        user1_credentials['password'], user1_credentials['cod_unidade'],
        header_admin)

@pytest.fixture(scope="module")
def register_user_2(
    client: Session,
    truncate_users,
    register_admin,
    header_admin: dict,
    user2_credentials: dict
    ) -> HTTPResponse:
    return register_user(client, user2_credentials['username'],
        user2_credentials['password'], user2_credentials['cod_unidade'],
        header_admin)

@pytest.fixture(scope="module")
def header_not_logged_in() -> dict:
    return prepare_header(username=None, password=None)

@pytest.fixture(scope="module")
def header_admin(register_admin, admin_credentials: dict) -> dict:
    return prepare_header(
        username=admin_credentials['username'],
        password=admin_credentials['password'])

@pytest.fixture(scope="module")
def header_usr_1(register_user_1, user1_credentials: dict) -> dict:
    """Authenticate in the API as user1 and return a dict with bearer
    header parameter to be passed to apis requests."""
    #TODO: Refatorar e resolver utilizando o objeto TestClient
    # data = {
    #     'grant_type': '',
    #     'username': 'nitai@example.com',
    #     'password': 'string',
    #     'scope': '',
    #     'client_id': '',
    #     'client_secret': ''
    # }
    # response = client.post(f"/auth/jwt/login", data=data)
    # print(response)
    # return response.json().get("access_token")

    # shell_cmd = 'curl -X POST "http://192.168.0.206:5057/auth/jwt/login"' \
    #                 ' -H  "accept: application/json"' \
    #                 ' -H  "Content-Type: application/json"' \
    #                 ' -d "grant_type=&username=test1%40api.com&password=api&scope=&client_id=&client_secret="'
    # my_cmd = os.popen(shell_cmd).read()
    # response = json.loads(my_cmd)
    # token_user_1 = response.get('access_token')
    return prepare_header(
        username=user1_credentials['username'],
        password=user1_credentials['password'])

@pytest.fixture(scope="module")
def header_usr_2(register_user_2, user2_credentials: dict) -> dict:
    """Authenticate in the API as user2 and return a dict with bearer
    header parameter to be passed to apis requests."""
    return prepare_header(
        username=user2_credentials['username'],
        password=user2_credentials['password'])

# @pytest.fixture(scope="module")
# def insert_pt_user_1(header_usr_1, client):
#     client.put(f"/plano_trabalho/888888888",
#                json=input_pt,
#                headers=header_usr_1)


# Tests

def test_register_user_not_logged_in(
        truncate_users, client: Session, header_not_logged_in: dict):
    user_1 = register_user(client, "testx@api.com", "api", 0, header_not_logged_in)
    assert user_1.status_code == status.HTTP_401_UNAUTHORIZED

def test_register_user(truncate_users, client: Session, header_admin: dict):
    user_1 = register_user(client, "testx@api.com", "api", 0, header_admin)
    assert user_1.status_code == status.HTTP_201_CREATED

    user_2 = register_user(client, "testx@api.com", "api", 0, header_admin)
    assert user_2.status_code == status.HTTP_400_BAD_REQUEST
    assert user_2.json().get("detail", None) == "REGISTER_USER_ALREADY_EXISTS"

def test_authenticate(header_usr_1: dict):
    token = header_usr_1.get("Authorization")
    assert isinstance(token, str)
    assert "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9." in token

def test_get_user_self_not_logged_in(client: Session,
        header_not_logged_in: dict):
    response = client.get('/users/me', headers=header_not_logged_in)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_user_self_logged_in(client: Session, user1_credentials: dict,
        header_usr_1: dict):
    response = client.get('/users/me', headers=header_usr_1)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data.get("email", None) == user1_credentials['username']
    assert data.get("cod_unidade", None) == user1_credentials['cod_unidade']
    assert data.get("is_active", None) == True

def test_patch_user_self_change_cod_unidade(client: Session,
        header_usr_1: dict):
    " Testa se o usuário pode alterar o seu próprio cod_unidade."
    response = client.patch(
        '/users/me',
        json={'cod_unidade': 3},
        headers=header_usr_1
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_create_plano_trabalho_completo(input_pt: dict,
                                        header_usr_1: dict,
                                        truncate_pt,
                                        client: Session):
    response = client.put(f"/plano_trabalho/555",
                          json=input_pt,
                          headers=header_usr_1)

    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("detail", None) == None
    assert response.json() == input_pt

@pytest.mark.parametrize("omitted_fields",
                         enumerate((
                             ["data_interrupcao"],
                             ["data_interrupcao", "entregue_no_prazo"],
                             ["entregue_no_prazo"],
                         )))
def test_create_plano_trabalho_omit_optional_fields(input_pt: dict,
                                             omitted_fields: list,
                                             header_usr_1: dict,
                                             truncate_pt,
                                             client: Session):
    offset, field_list = omitted_fields
    for field in field_list:
        del input_pt[field]

    input_pt['cod_plano'] = 557 + offset
    response = client.put(f"/plano_trabalho/{input_pt['cod_plano']}",
                          json=input_pt,
                          headers=header_usr_1)
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.parametrize("missing_fields",
                         enumerate((
                             ["matricula_siape"],
                             ["cpf"],
                             ["nome_participante"],
                             ["cod_unidade_exercicio"],
                             ["nome_unidade_exercicio"],
                             ["modalidade_execucao"],
                             ["carga_horaria_semanal"],
                             ["data_inicio"],
                             ["data_fim"],
                             ["carga_horaria_total"],
                         )))
def test_create_plano_trabalho_missing_mandatory_fields(input_pt: dict,
                                             missing_fields: list,
                                             header_usr_1: dict,
                                             truncate_pt,
                                             client: Session):
    """Tenta criar um plano de trabalho, faltando campos obrigatórios.
    Tem que ser um plano de trabalho novo, pois na atualização de um
    plano de trabalho existente, o campo que ficar faltando será
    interpretado como um campo que não será atualizado, ainda que seja
    obrigatório para a criação.
    """
    offset, field_list = missing_fields
    for field in field_list:
        del input_pt[field]

    input_pt['cod_plano'] = 1800 + offset # precisa ser um novo plano
    response = client.put(f"/plano_trabalho/{input_pt['cod_plano']}",
                          json=input_pt,
                          headers=header_usr_1)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.parametrize("missing_fields",
                         (
                             ["matricula_siape"],
                             ["cpf"],
                             ["nome_participante"],
                             ["cod_unidade_exercicio"],
                             ["nome_unidade_exercicio"],
                             ["modalidade_execucao"],
                             ["carga_horaria_semanal"],
                             ["data_inicio"],
                             ["data_fim"],
                             ["carga_horaria_total"],
                         ))
def test_update_plano_trabalho_missing_mandatory_fields(example_pt,
                                            input_pt: dict,
                                            missing_fields: list,
                                            header_usr_1: dict,
                                            client: Session):
    """Tenta atualizar um plano de trabalho, faltando campos
    obrigatórios. Tem que ser um plano de trabalho existente para ser
    interpretado como update. O campo que ficar faltando será
    interpretado como um campo que não será atualizado, ainda que seja
    obrigatório no momento de sua criação.
    """
    for field in missing_fields:
        del input_pt[field]

    input_pt['cod_plano'] = 555 # precisa ser um plano existente
    response = client.put(f"/plano_trabalho/{input_pt['cod_plano']}",
                          json=input_pt,
                          headers=header_usr_1)
    assert response.status_code == status.HTTP_200_OK

def test_create_pt_cod_plano_inconsistent(input_pt: dict,
                                          header_usr_1: dict,
                                          truncate_pt,
                                          client: Session):
    input_pt["cod_plano"] = 110
    response = client.put("/plano_trabalho/111", # diferente de 110
                          json=input_pt,
                          headers=header_usr_1)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    detail_msg = "Parâmetro cod_plano diferente do conteúdo do JSON"
    assert response.json().get("detail", None) == detail_msg

def test_get_plano_trabalho(header_usr_1: dict,
                            truncate_pt,
                            example_pt,
                            client: Session):
    response = client.get("/plano_trabalho/555",
                          headers=header_usr_1)
    assert response.status_code == status.HTTP_200_OK

def test_get_pt_inexistente(header_usr_1: dict, client: Session):
    response = client.get("/plano_trabalho/888888888",
                          headers=header_usr_1)
    assert response.status_code == 404

    assert response.json().get("detail", None) == "Plano de trabalho não encontrado"

@pytest.mark.parametrize("data_inicio, data_fim, cod_plano, id_ati_1, id_ati_2",
                          [
                            ("2020-06-04", "2020-04-01", '77', 333, 334),
                            ("2020-06-04", "2020-04-01", '78', 335, 336),
                            ("2020-06-04", "2020-04-01", '79', 337, 338),
                            ])
def test_create_pt_invalid_dates(input_pt: dict,
                                 data_inicio: str,
                                 data_fim: str,
                                 cod_plano: str,
                                 id_ati_1: int,
                                 id_ati_2: int,
                                 header_usr_1: dict,
                                 truncate_pt,
                                 client: Session):
    input_pt['data_inicio'] = data_inicio
    input_pt['data_fim'] = data_fim
    input_pt['cod_plano'] = cod_plano
    input_pt['atividades'][0]['id_atividade'] = id_ati_1
    input_pt['atividades'][1]['id_atividade'] = id_ati_2

    response = client.put(f"/plano_trabalho/{cod_plano}",
                          json=input_pt,
                          headers=header_usr_1)
    if data_inicio > data_fim:
        assert response.status_code == 422
        detail_msg = "Data fim do Plano de Trabalho deve ser maior" \
                     " ou igual que Data início."
        assert response.json().get("detail")[0]["msg"] == detail_msg
    else:
        assert response.status_code == status.HTTP_200_OK

@pytest.mark.parametrize(
    "dt_fim, dt_avaliacao_1, dt_avaliacao_2, cod_plano, id_ati_1, id_ati_2",
    [
      ("2020-06-04", "2020-04-01", "2020-04-01", '77', 333, 334),
      ("2020-06-04", "2020-04-01", "2021-04-01", '78', 335, 336),
      ("2020-06-04", "2020-04-01", "2019-04-01", '79', 337, 338),
      ("2020-04-01", "2020-04-01", "2020-06-04", '80', 339, 340),
      ("2020-04-01", "2020-04-01", "2020-04-01", '81', 341, 342),
      ("2020-04-01", "2020-02-01", "2020-01-04", '82', 343, 344),
      ])
def test_create_pt_invalid_data_avaliacao(input_pt: dict,
                                          dt_fim: str,
                                          dt_avaliacao_1: str,
                                          dt_avaliacao_2: str,
                                          cod_plano: dict,
                                          id_ati_1: int,
                                          id_ati_2: int,
                                          header_usr_1: dict,
                                          truncate_pt,
                                          client: Session):
    input_pt['data_inicio'] = "2020-01-01"
    input_pt['data_fim'] = dt_fim
    input_pt['cod_plano'] = cod_plano
    input_pt['atividades'][0]['id_atividade'] = id_ati_1
    input_pt['atividades'][0]['data_avaliacao'] = dt_avaliacao_1
    input_pt['atividades'][1]['id_atividade'] = id_ati_2
    input_pt['atividades'][1]['data_avaliacao'] = dt_avaliacao_2

    response = client.put(f"/plano_trabalho/{cod_plano}",
                          json=input_pt,
                          headers=header_usr_1)
    if dt_fim > dt_avaliacao_1 or dt_fim > dt_avaliacao_2:
        assert response.status_code == 422
        detail_msg = "Data de avaliação da atividade deve ser maior ou igual" \
                     " que a Data Fim do Plano de Trabalho."
        assert response.json().get("detail")[0]["msg"] == detail_msg
    else:
        assert response.status_code == status.HTTP_200_OK

@pytest.mark.parametrize("cod_plano, id_ati_1, id_ati_2",
                          [
                            ('90', 401, 402),
                            ('91', 403, 403), # <<<< IGUAIS
                            ('92', 404, 404), # <<<< IGUAIS
                            ('93', 405, 406),
                            ])
def test_create_pt_duplicate_atividade(input_pt: dict,
                                       cod_plano: str,
                                       id_ati_1: int,
                                       id_ati_2: int,
                                       header_usr_1: dict,
                                       truncate_pt,
                                       client: Session):
    input_pt['cod_plano'] = cod_plano
    input_pt['atividades'][0]['id_atividade'] = id_ati_1
    input_pt['atividades'][1]['id_atividade'] = id_ati_2

    response = client.put(f"/plano_trabalho/{cod_plano}",
                          json=input_pt,
                          headers=header_usr_1)
    if id_ati_1 == id_ati_2:
        assert response.status_code == 422
        detail_msg = "Atividades devem possuir id_atividade diferentes."
        assert response.json().get("detail")[0]["msg"] == detail_msg
    else:
        assert response.status_code == status.HTTP_200_OK

def test_update_pt_different_cod_unidade(input_pt: dict,
                                         header_usr_2: dict,
                                         client: Session):
    cod_plano = 555
    response = client.put(f"/plano_trabalho/{cod_plano}",
                          json=input_pt,
                          headers=header_usr_2)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    detail_msg = "Usuário não pode alterar Plano de Trabalho de outra unidade."
    assert response.json().get("detail", None) == detail_msg

@pytest.mark.parametrize("cod_plano, cpf",
                          [
                            ('100', '11111111111'),
                            ('101', '22222222222'),
                            ('102', '33333333333'),
                            ('103', '44444444444'),
                            ('104', '04811556435'),
                            ('103', '444-444-444.44'),
                            ('108', '-44444444444'),
                            ('111', '444444444'),
                            ('112', '-444 4444444'),
                            ('112', '4811556437'),
                            ('112', '048115564-37'),
                            ('112', '04811556437     '),
                            ('112', '    04811556437     '),
                            ('112', ''),
                            ])
def test_create_pt_invalid_cpf(input_pt: dict,
                               cod_plano: str,
                               cpf: str,
                               header_usr_1: dict,
                               truncate_pt,
                               client: Session):
    input_pt['cod_plano'] = cod_plano
    input_pt['cpf'] = cpf

    response = client.put(f"/plano_trabalho/{cod_plano}",
                          json=input_pt,
                          headers=header_usr_1)
    assert response.status_code == 422
    detail_msg = [
        'Digitos verificadores do CPF inválidos.',
        'CPF inválido.',
        'CPF precisa ter 11 digitos.',
        'CPF deve conter apenas digitos.',
    ]
    assert response.json().get("detail")[0]["msg"] in detail_msg


@pytest.mark.parametrize("cod_plano, modalidade_execucao",
                          [
                            ('556', -1),
                            ('81', -2),
                            ('82', -3)
                            ])
def test_create_pt_invalid_modalidade_execucao(input_pt: dict,
                               cod_plano: str,
                               modalidade_execucao: int,
                               header_usr_1: dict,
                               truncate_pt,
                               client: Session):
    input_pt['cod_plano'] = cod_plano
    input_pt['modalidade_execucao'] = modalidade_execucao
    response = client.put(f"/plano_trabalho/{cod_plano}",
                          json=input_pt,
                          headers=header_usr_1)

    assert response.status_code == 422
    detail_msg = "value is not a valid enumeration member; permitted: 1, 2, 3"
    assert response.json().get("detail")[0]["msg"] == detail_msg

@pytest.mark.parametrize("carga_horaria_semanal",
                          [
                            (56),
                            (-2),
                            (0),
                            ])
def test_create_pt_invalid_carga_horaria_semanal(input_pt: dict,
                                                 carga_horaria_semanal: int,
                                                 header_usr_1: dict,
                                                 truncate_pt,
                                                 client: Session):
    cod_plano = '767676'
    input_pt['cod_plano'] = cod_plano
    input_pt['carga_horaria_semanal'] = carga_horaria_semanal
    response = client.put(f"/plano_trabalho/{cod_plano}",
                          json=input_pt,
                          headers=header_usr_1)

    assert response.status_code == 422
    detail_msg = "Carga horária semanal deve ser entre 1 e 40"
    assert response.json().get("detail")[0]["msg"] == detail_msg


@pytest.mark.parametrize("carga_horaria_total, tempo_pres_1, tempo_tel_1, tempo_pres_2, tempo_tel_2",
                          [(56, 2, 3, 4, 5),
                           (-2, 2, 3, 4.3, 5),
                           (0, 2, 3, 4.2, 5),
                           ])
def test_create_pt_invalid_carga_horaria_total(input_pt: dict,
                                                 carga_horaria_total: float,
                                                 tempo_pres_1: float,
                                                 tempo_tel_1: float,
                                                 tempo_pres_2: float,
                                                 tempo_tel_2: float,
                                                 header_usr_1: dict,
                                                 truncate_pt,
                                                 client: Session):
    cod_plano = 767677
    input_pt['cod_plano'] = cod_plano
    input_pt['carga_horaria_total'] = carga_horaria_total
    input_pt['atividades'][0]['tempo_exec_presencial'] = tempo_pres_1
    input_pt['atividades'][0]['tempo_exec_teletrabalho'] = tempo_tel_1
    input_pt['atividades'][1]['tempo_exec_presencial'] = tempo_pres_2
    input_pt['atividades'][1]['tempo_exec_teletrabalho'] = tempo_tel_2

    response = client.put(f"/plano_trabalho/{cod_plano}",
                          json=input_pt,
                          headers=header_usr_1)

    assert response.status_code == 422
    detail_msg = 'A soma dos tempos de execução presencial e ' \
                 'teletrabalho das atividades deve ser igual à ' \
                 'carga_horaria_total.'
    assert response.json().get("detail")[0]["msg"] == detail_msg

@pytest.mark.parametrize(
    "id_atividade, nome_atividade, faixa_complexidade, "\
    "tempo_exec_presencial, tempo_exec_teletrabalho, qtde_entregas",
                          [
                              (None, 'asd', 'asd', 0, 0, 3),
                              (123123, None, 'asd', 0, 0, 3),
                              (123123, 'asd', None, 0, 0, 3),
                              (123123, 'asd', 'asd', None, 0, 3),
                              (123123, 'asd', 'asd', 0, None, 3),
                              (123123, 'asd', 'asd', 0, 0, None),
                           ])
def test_create_pt_missing_mandatory_fields_atividade(input_pt: dict,

                                           id_atividade: int,
                                           nome_atividade: str,
                                           faixa_complexidade: str,
                                           tempo_exec_presencial: float,
                                           tempo_exec_teletrabalho: float,
                                           qtde_entregas: int,

                                           header_usr_1: dict,
                                           truncate_pt,
                                           client: Session):
    cod_plano = '111222333'
    input_pt['cod_plano'] = cod_plano
    input_pt['atividades'][0]['id_atividade'] = id_atividade
    input_pt['atividades'][0]['nome_atividade'] = nome_atividade
    input_pt['atividades'][0]['faixa_complexidade'] = faixa_complexidade
    input_pt['atividades'][0]['tempo_exec_presencial'] = tempo_exec_presencial
    input_pt['atividades'][0]['tempo_exec_teletrabalho'] = tempo_exec_teletrabalho
    input_pt['atividades'][0]['qtde_entregas'] = qtde_entregas

    response = client.put(f"/plano_trabalho/{cod_plano}",
                          json=input_pt,
                          headers=header_usr_1)
    assert response.status_code == 422
    #TODO: Melhorar resposta automática do Pydantic para deixar claro qual campo não passou na validação
    detail_msg = 'none is not an allowed value'
    assert response.json().get("detail")[0]["msg"] == detail_msg
