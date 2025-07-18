permissions = [
    # Legal Entity Company Relations
    (
        "add_legal_entity_company_relation",
        "Добавление legal_entity_company_relation",
        "reference_app, crm_app, contract_app",
    ),
    (
        "edit_legal_entity_company_relation",
        "Редкатирование legal_entity_company_relation",
        "reference_app, crm_app, contract_app",
    ),
    (
        "delete_legal_entity_company_relation",
        "Удаление legal_entity_company_relation",
        "reference_app, crm_app, contract_app",
    ),
    (
        "view_legal_entity_company_relation",
        "Просмотр legal_entity_company_relation",
        "reference_app, crm_app, contract_app",
    ),
    (
        "get_all_legal_entity_company_relations",
        "Просмотр всех legal_entity_company_relationов",
        "reference_app, crm_app, contract_app",
    ),
    # User Company Relations
    ("add_user_company_relation", "Добавление user_company_relation", "all"),
    ("edit_user_company_relation", "Редкатирование user_company_relation", "all"),
    ("delete_user_company_relation", "Удаление user_company_relation", "all"),
    ("view_user_company_relation", "Просмотр user_company_relation", "all"),
    ("get_all_user_company_relations", "Просмотр всех user_company_relationов", "all"),
    # Templates
    ("add_template", "Добавление шаблона", "crm_app"),
    ("edit_template", "Редактирование шаблона", "crm_app"),
    ("delete_template", "Удаление шаблона", "crm_app"),
    ("view_template", "Просмотр шаблона", "crm_app"),
    ("download_template", "Скачивание шаблона", "crm_app"),
    ("generate_template", "Генерация документа по шаблону", "crm_app"),
    ("get_all_templates", "Просмотр всех шаблонов", "crm_app"),
    # Bank Accounts
    ("add_bank_account", "Добавление банковского счета", "crm_app"),
    ("edit_bank_account", "Редкатирование банковского счета", "crm_app"),
    ("delete_bank_account", "Удаление банковского счета", "crm_app"),
    ("view_bank_account", "Просмотр банковского счета", "crm_app"),
    ("get_all_bank_accounts", "Просмотр всех банковских счетов", "crm_app"),
    # Services
    ("add_service", "Добавление услуги", "crm_app"),
    ("edit_service", "Редкатирование услуги", "crm_app"),
    ("delete_service", "Удаление услуги", "crm_app"),
    ("view_service", "Просмотр услуги", "crm_app"),
    ("get_all_services", "Просмотр всех услуг", "crm_app"),
    # Users
    ("add_user", "Добавление пользователя", "all"),
    ("edit_user", "Редактирование пользователя", "all"),
    ("delete_user", "Удаление пользователя", "all"),
    ("view_user", "Просмотр пользователя", "all"),
    ("get_all_users", "Просмотр всех пользователей", "all"),
    # Companies
    ("add_company", "Добавление компании", "all"),
    ("edit_company", "Редактирование компании", "all"),
    ("delete_company", "Удаление компании", "all"),
    ("view_company", "Просмотр компании", "all"),
    ("get_all_companies", "Просмотр всех компаний", "all"),
    # Contracts
    ("add_contract", "Добавление договора", "contract_app, crm_app"),
    ("edit_contract", "Редактирование договора", "contract_app, crm_app"),
    ("delete_contract", "Удаление договора", "contract_app, crm_app"),
    ("view_contract", "Просмотр договора", "contract_app, crm_app"),
    ("get_all_contracts", "Просмотр всех договоров", "contract_app, crm_app"),
    ("download_contract", "Скачивание договора", "contract_app, crm_app"),
    # Legal Entities
    ("add_legal_entity", "Добавление юридического лица", "reference_app, crm_app, contract_app"),
    ("edit_legal_entity", "Редактирование юридического лица", "reference_app, crm_app, contract_app"),
    (
        "add_legal_entity_by_inn",
        "Добавление юр. лица по инн и кпп",
        "reference_app, crm_app, contract_app",
    ),
    ("delete_legal_entity", "Удаление юридического лица", "reference_app, crm_app, contract_app"),
    ("view_legal_entity", "Просмотр юридического лица", "reference_app, crm_app, contract_app"),
    (
        "get_all_legal_entities",
        "Просмотр всех юридических лиц",
        "reference_app, crm_app, contract_app",
    ),
    (
        "get_sellers",
        "Просмотр всех юридических лиц типа seller компании",
        "reference_app, crm_app, contract_app",
    ),
    (
        "get_buyers",
        "Просмотр всех юридических лиц типа buyer компании",
        "reference_app, crm_app, contract_app",
    ),
    (
        "get_by_company",
        "Просмотр всех юридических лиц по компании",
        "reference_app, crm_app, contract_app",
    ),
    (
        "get_legal_entity_by_inn_kpp",
        "Получение юр. лиц по инн, кпп",
        "reference_app, crm_app, contract_app",
    ),
    # Bills
    ("add_bill", "Добавление счёта", "crm_app"),
    ("edit_bill", "Редактирование счёта", "crm_app"),
    ("delete_bill", "Удаление счёта", "crm_app"),
    ("view_bill", "Просмотр счёта", "crm_app"),
    ("get_all_bills", "Просмотр всех счетов", "crm_app"),
    # BillDetails
    ("add_bill_detail", "Добавление позиции счёта", "crm_app"),
    ("edit_bill_detail", "Редактирование позиции счёта", "crm_app"),
    ("delete_bill_detail", "Удаление позиции счёта", "crm_app"),
    ("view_bill_detail", "Просмотр позиции счёта", "crm_app"),
    ("get_all_bill_details", "Просмотр всех позиций счетов", "crm_app"),
    # Acts
    ("add_act", "Добавление акта", "crm_app"),
    ("edit_act", "Редактирование акта", "crm_app"),
    ("delete_act", "Удаление акта", "crm_app"),
    ("view_act", "Просмотр акта", "crm_app"),
    ("get_all_acts", "Просмотр всех актов", "crm_app"),
    # ActDetails
    ("add_act_detail", "Добавление позиции акта", "crm_app"),
    ("edit_act_detail", "Редактирование позиции акта", "crm_app"),
    ("delete_act_detail", "Удаление позиции акта", "crm_app"),
    ("view_act_detail", "Просмотр позиции акта", "crm_app"),
    ("get_all_act_details", "Просмотр всех позиций актов", "crm_app"),
    # API tokens:
    ("add_api_token", "Добавление API токена", "all"),
    ("edit_api_token", "Редактирование API токена", "all"),
    ("delete_api_token", "Удаление API токена", "all"),
    ("view_api_token", "Просмотр API токена", "all"),
    ("get_all_api_tokens", "Просмотр всех API токенов", "all"),
    # Web hooks
    ("set_webhook", "Добавление вебхука", "observer_app"),
    ("delete_webhook", "Удаление вебхука", "observer_app"),
    ("view_webhook_info", "Просмотр информации о вебхуке", "observer_app"),
    # Bots:
    ("add_bot", "Добавление бота", "observer_app"),
    ("delete_bot", "Удаление бота", "observer_app"),
    ("view_bot", "Просмотр бота", "observer_app"),
    ("get_all_bots", "Просмотр всех ботов", "observer_app"),
    # Get:
    ("get_all_chats", "Просмотр всех чатов", "observer_app"),
    ("get_all_accounts", "Просмотр всех тг аккаунтов", "observer_app"),
    # Prompts
    ("add_prompt", "Добавление промпта", "observer_app"),
    ("edit_prompt", "Редактирование промпта", "observer_app"),
    ("delete_prompt", "Удаление промпта", "observer_app"),
    ("view_prompt", "Просмотр промпта", "observer_app"),
    ("get_all_prompts", "Просмотр всех промптов", "observer_app"),
    # Schedules
    ("add_schedule", "Добавление расписания", "observer_app"),
    ("toggle_schedule", "Отключение/включение расписания", "observer_app"),
    ("edit_schedule", "Редактирование расписания", "observer_app"),
    ("delete_schedule", "Удаление расписания", "observer_app"),
    ("view_schedule", "Просмотр расписания", "observer_app"),
    ("get_all_schedules", "Просмотр всех расписаний", "observer_app"),
    # Analysis
    ("create_analysis", "Создание анализа", "observer_app"),
    ("view_analysis", "Просмотр анализа", "observer_app"),
    ("get_all_analyses", "Просмотр всех анализов", "observer_app"),
    # Warehouses
    ("add_warehouse", "Добавление склада", "reference_app"),
    ("edit_warehouse", "Редактирование склада", "reference_app"),
    ("delete_warehouse", "Удаление склада", "reference_app"),
    ("view_warehouse", "Просмотр склада", "reference_app"),
    ("get_all_warehouses", "Просмотр всех складов", "reference_app"),
    # Cash Registers
    ("add_cash_register", "Добавление кассы", "reference_app"),
    ("edit_cash_register", "Редактирование кассы", "reference_app"),
    ("delete_cash_register", "Удаление кассы", "reference_app"),
    ("view_cash_register", "Просмотр кассы", "reference_app"),
    ("get_all_cash_registers", "Просмотр всех касс", "reference_app"),
    # Cities
    ("add_city", "Добавление города", "reference_app"),
    ("edit_city", "Редактирование города", "reference_app"),
    ("delete_city", "Удаление города", "reference_app"),
    ("view_city", "Просмотр города", "reference_app"),
    ("get_all_cities", "Просмотр всех городов", "reference_app"),
    # Contract files
    ("add_contract_file", "Добавление файла контракта", "contract_app"),
    ("edit_contract_file", "Редактирование файла контракта", "contract_app"),
    ("delete_contract_file", "Удаление файла контракта", "contract_app"),
    ("view_contract_file", "Просмотр файла контракта", "contract_app"),
    ("get_all_contract_files", "Просмотр всех файлов контрактов", "contract_app"),
    # Contract Types
    ("get_all_contract_types", "Просмотр всех типов контрактов", "contract_app"),
    # Parcels
    ("add_parcel", "Добавление накладной", "parcel_app"),
    ("edit_parcel", "Редактирование накладной", "parcel_app"),
    ("delete_parcel", "Удаление накладной", "parcel_app"),
    ("view_parcel", "Просмотр накладной", "parcel_app"),
    ("get_parcel_current_status", "Просмотр нынешнего статуса накладной", "parcel_app"),
    ("get_all_parcels", "Просмотр всех накладных", "parcel_app"),
    # Parcel products
    ("add_parcel_product", "Добавление товара накладной", "parcel_app"),
    ("edit_parcel_product", "Редактирование товара накладной", "parcel_app"),
    ("delete_parcel_product", "Удаление товара накладной", "parcel_app"),
    ("view_parcel_product", "Просмотр товара накладной", "parcel_app"),
    ("get_all_parcel_products", "Просмотр всех товаров накладных", "parcel_app"),
    # Parcel cargo
    ("add_parcel_cargo", "Добавление груза накладной", "parcel_app"),
    ("edit_parcel_cargo", "Редактирование груза накладной", "parcel_app"),
    ("delete_parcel_cargo", "Удаление груза накладной", "parcel_app"),
    ("view_parcel_cargo", "Просмотр груза накладной", "parcel_app"),
    ("get_all_parcel_cargo", "Просмотр всех грузов накладных", "parcel_app"),
    # Parcel status
    ("view_parcel_status", "Просмотр статуса накладной", "parcel_app"),
    ("get_all_parcel_statuses", "Просмотр всех статусов накладных", "parcel_app"),
    # Arrival to warehouse
    ("add_arrival", "Добавление прибытия", "parcel_app"),
    ("edit_arrival", "Редактирование прибытия", "parcel_app"),
    ("delete_arrival", "Удаление прибытия", "parcel_app"),
    ("view_arrival", "Просмотр прибытия", "parcel_app"),
    ("get_all_arrivals", "Просмотр всех прибытий", "parcel_app"),
    # Arrival details
    ("add_arrival_details", "Добавление детали прибытия", "parcel_app"),
    ("edit_arrival_details", "Редактирование детали прибытия", "parcel_app"),
    ("delete_arrival_details", "Удаление детали прибытия", "parcel_app"),
    ("view_arrival_details", "Просмотр детали прибытия", "parcel_app"),
    ("get_all_arrival_details", "Просмотр всех деталей прибытий", "parcel_app"),
    # Delivery to recipient
    ("add_delivery", "Добавление доставки клиенту", "parcel_app"),
    ("edit_delivery", "Редактирование доставки клиенту", "parcel_app"),
    ("delete_delivery", "Удаление доставки клиенту", "parcel_app"),
    ("view_delivery", "Просмотр доставки клиенту", "parcel_app"),
    (
        "get_all_deliveries",
        "Просмотр всех доставок клиенту",
        "parcel_app",
    ),
    # Issue to employee
    ("add_issue", "Добавление передачи курьеру", "parcel_app"),
    ("edit_issue", "Редактирование передачи курьеру", "parcel_app"),
    ("delete_issue", "Удаление передачи курьеру", "parcel_app"),
    ("view_issue", "Просмотр передачи курьеру", "parcel_app"),
    (
        "get_all_issues",
        "Просмотр всех передач курьеру",
        "parcel_app",
    ),
    # Issue details
    ("add_issue_details", "Добавление детали передачи курьеру", "parcel_app"),
    ("edit_issue_details", "Редактирование детали передачи курьеру", "parcel_app"),
    ("delete_issue_details", "Удаление детали передачи курьеру", "parcel_app"),
    ("view_issue_details", "Просмотр детали передачи курьеру", "parcel_app"),
    (
        "get_all_issue_details",
        "Просмотр всех деталей передач курьеру",
        "parcel_app",
    ),
    # Pickup from sender
    ("add_pickup", "Добавление забора от отправителя", "parcel_app"),
    ("edit_pickup", "Редактирование забора от отправителя", "parcel_app"),
    ("delete_pickup", "Удаление забора от отправителя", "parcel_app"),
    ("view_pickup", "Просмотр забора от отправителя", "parcel_app"),
    (
        "get_all_pickups",
        "Просмотр всех заборов от отправителя",
        "parcel_app",
    ),
    # Return to sender
    ("add_return", "Добавление возврата отправителю", "parcel_app"),
    ("edit_return", "Редактирование возврата отправителю", "parcel_app"),
    ("delete_return", "Удаление возврата отправителю", "parcel_app"),
    ("view_return", "Просмотр возврата отправителю", "parcel_app"),
    (
        "get_all_returns",
        "Просмотр всех возвратов отправителю",
        "parcel_app",
    ),
    # Return detailsr
    ("add_return_details", "Добавление детали возврата отправителю", "parcel_app"),
    ("edit_return_details", "Редактирование детали возврата отправителю", "parcel_app"),
    ("delete_return_details", "Удаление детали возврата отправителю", "parcel_app"),
    ("view_return_details", "Просмотр детали возврата отправителю", "parcel_app"),
    (
        "get_all_return_details",
        "Просмотр всех деталей возвратов отправителю",
        "parcel_app",
    ),
    # Transit
    ("add_transit", "Добавление отправления", "parcel_app"),
    ("edit_transit", "Редактирование отправления", "parcel_app"),
    ("delete_transit", "Удаление отправления", "parcel_app"),
    ("view_transit", "Просмотр отправления", "parcel_app"),
    (
        "get_all_transits",
        "Просмотр всех отправлений",
        "parcel_app",
    ),
    # Transit details
    ("add_transit_details", "Добавление деталей отправления", "parcel_app"),
    ("edit_transit_details", "Редактирование деталей отправления", "parcel_app"),
    ("delete_transit_details", "Удаление деталей отправления", "parcel_app"),
    ("view_transit_details", "Просмотр деталей отправления", "parcel_app"),
    (
        "get_all_transit_details",
        "Просмотр всех деталей отправлений",
        "parcel_app",
    ),
    # Price categories
    ("add_price_category", "Добавление категории цен", "price_app"),
    ("edit_price_category", "Редактирование категории цен", "price_app"),
    ("delete_price_category", "Удаление категории цен", "price_app"),
    ("view_price_category", "Просмотр категории цен", "price_app"),
    (
        "get_all_price_categories",
        "Просмотр всех категорий цен",
        "price_app",
    ),
    # Price categories
    ("add_price", "Добавление цены", "price_app"),
    ("edit_price", "Редактирование цены", "price_app"),
    ("delete_price", "Удаление цены", "price_app"),
    ("view_price", "Просмотр цены", "price_app"),
    (
        "get_all_prices",
        "Просмотр всех цен",
        "price_app",
    ),
    # Price details
    ("add_price_detail", "Добавление детали цены", "price_app"),
    ("edit_price_detail", "Редактирование детали цены", "price_app"),
    ("delete_price_detail", "Удаление детали цены", "price_app"),
    ("view_price_detail", "Просмотр детали цены", "price_app"),
    (
        "get_all_price_details",
        "Просмотр всех деталей цен",
        "price_app",
    ),
    # Price sets
    ("add_price_set", "Добавление набора цен", "price_app"),
    ("edit_price_set", "Редактирование набора цен", "price_app"),
    ("delete_price_set", "Удаление набора цен", "price_app"),
    ("view_price_set", "Просмотр набора цен", "price_app"),
    (
        "get_all_price_sets",
        "Просмотр всех наборов цен",
        "price_app",
    ),
    # Price sets
    ("add_price_set_relation", "Добавление отношеня цена набор", "price_app"),
    ("edit_price_set_relation", "Редактирование отношеня цена набор", "price_app"),
    ("delete_price_set_relation", "Удаление отношеня цена набор", "price_app"),
    ("view_price_set_relation", "Просмотр отношеня цена набор", "price_app"),
    (
        "get_all_price_set_relations",
        "Просмотр всех отношений цена набор",
        "price_app",
    ),
]


async def add_initial_permissions():
    from app.database.models import Permission

    for permission in permissions:
        permission_id = permission[0]
        permission_name = permission[1]
        permission_comment = permission[2] if len(permission) > 2 else None

        try:
            obj, _ = await Permission.update_or_create(
                defaults={"name": permission_name, "comment": permission_comment},
                id=permission_id,
            )
        except Exception as e:
            print(f"Ошибка при создании/обновлении {permission_id}: {e}")
