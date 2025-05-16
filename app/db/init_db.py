import logging
from sqlalchemy import select, insert
from app.db.base import async_session_factory
from app.db.models import (
    Building,
    Activity,
    Organization,
    PhoneNumber,
    organization_activity,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db():
    logger.info("Creating initial test data...")

    async with async_session_factory() as db:
        result = await db.execute(select(Building))
        if result.scalars().first():
            logger.info("Database already contains data, skipping initialization")
            return

        try:
            logger.info("Creating buildings...")
            buildings = [
                Building(
                    name="Деловой центр",
                    address="г. Москва, ул. Ленина 1, офис 3",
                    latitude=55.7558,
                    longitude=37.6173,
                ),
                Building(
                    name="Технопарк",
                    address="г. Санкт-Петербург, Невский проспект 78",
                    latitude=59.9311,
                    longitude=30.3609,
                ),
                Building(
                    name="Бизнес-центр Блюхера",
                    address="г. Новосибирск, ул. Блюхера, 32/1",
                    latitude=55.0415,
                    longitude=82.9346,
                ),
                Building(
                    name="Центральный офис",
                    address="г. Екатеринбург, ул. Малышева 51",
                    latitude=56.8389,
                    longitude=60.6057,
                ),
                Building(
                    name="Офисная башня",
                    address="г. Казань, ул. Баумана 38",
                    latitude=55.7879,
                    longitude=49.1233,
                ),
            ]

            db.add_all(buildings)
            await db.commit()
            logger.info("Buildings created successfully")

           
            for building in buildings:
                await db.refresh(building)

            
            logger.info("Creating activity hierarchy...")

            
            food = Activity(name="Еда")
            auto = Activity(name="Автомобили")
            it = Activity(name="Информационные технологии")
            construction = Activity(name="Строительство")
            healthcare = Activity(name="Здравоохранение")

            db.add_all([food, auto, it, construction, healthcare])
            await db.commit()

            for activity in [food, auto, it, construction, healthcare]:
                await db.refresh(activity)

            meat_products = Activity(name="Мясная продукция", parent_id=food.id)
            dairy_products = Activity(name="Молочная продукция", parent_id=food.id)
            bakery = Activity(name="Хлебобулочные изделия", parent_id=food.id)

            trucks = Activity(name="Грузовые", parent_id=auto.id)
            passenger_cars = Activity(name="Легковые", parent_id=auto.id)

            software = Activity(name="Программное обеспечение", parent_id=it.id)
            hardware = Activity(name="Компьютерное оборудование", parent_id=it.id)

            materials = Activity(
                name="Строительные материалы", parent_id=construction.id
            )
            services = Activity(name="Строительные услуги", parent_id=construction.id)

            medical_services = Activity(
                name="Медицинские услуги", parent_id=healthcare.id
            )
            pharmaceuticals = Activity(name="Фармацевтика", parent_id=healthcare.id)

            db.add_all(
                [
                    meat_products,
                    dairy_products,
                    bakery,
                    trucks,
                    passenger_cars,
                    software,
                    hardware,
                    materials,
                    services,
                    medical_services,
                    pharmaceuticals,
                ]
            )
            await db.commit()

            second_level = [
                meat_products,
                dairy_products,
                bakery,
                trucks,
                passenger_cars,
                software,
                hardware,
                materials,
                services,
                medical_services,
                pharmaceuticals,
            ]
            for activity in second_level:
                await db.refresh(activity)

            beef = Activity(name="Говядина", parent_id=meat_products.id)
            pork = Activity(name="Свинина", parent_id=meat_products.id)

            milk = Activity(name="Молоко", parent_id=dairy_products.id)
            cheese = Activity(name="Сыр", parent_id=dairy_products.id)

            parts = Activity(name="Запчасти", parent_id=passenger_cars.id)
            accessories = Activity(name="Аксессуары", parent_id=passenger_cars.id)

            mobile_apps = Activity(name="Мобильные приложения", parent_id=software.id)
            web_apps = Activity(name="Веб-приложения", parent_id=software.id)

            computers = Activity(name="Компьютеры", parent_id=hardware.id)
            peripherals = Activity(name="Периферия", parent_id=hardware.id)

            cement = Activity(name="Цемент", parent_id=materials.id)
            bricks = Activity(name="Кирпич", parent_id=materials.id)

            db.add_all(
                [
                    beef,
                    pork,
                    milk,
                    cheese,
                    parts,
                    accessories,
                    mobile_apps,
                    web_apps,
                    computers,
                    peripherals,
                    cement,
                    bricks,
                ]
            )
            await db.commit()

            logger.info("Activities created successfully")

            logger.info("Creating organizations...")

            org1 = Organization(name='ООО "Рога и Копыта"', building_id=buildings[0].id)
            db.add(org1)
            await db.commit()
            await db.refresh(org1)

            phone1_1 = PhoneNumber(number="2-222-222", organization_id=org1.id)
            phone1_2 = PhoneNumber(number="3-333-333", organization_id=org1.id)
            phone1_3 = PhoneNumber(number="8-923-666-13-13", organization_id=org1.id)
            db.add_all([phone1_1, phone1_2, phone1_3])
            await db.commit()

            await db.execute(
                organization_activity.insert().values(
                    [
                        {"organization_id": org1.id, "activity_id": meat_products.id},
                        {"organization_id": org1.id, "activity_id": dairy_products.id},
                    ]
                )
            )
            await db.commit()

            org2 = Organization(name='ЗАО "Автомастер"', building_id=buildings[1].id)
            db.add(org2)
            await db.commit()
            await db.refresh(org2)

            phone2_1 = PhoneNumber(number="7-777-777", organization_id=org2.id)
            phone2_2 = PhoneNumber(number="8-800-555-35-35", organization_id=org2.id)
            db.add_all([phone2_1, phone2_2])
            await db.commit()

            await db.execute(
                organization_activity.insert().values(
                    [
                        {"organization_id": org2.id, "activity_id": passenger_cars.id},
                        {"organization_id": org2.id, "activity_id": parts.id},
                        {"organization_id": org2.id, "activity_id": accessories.id},
                    ]
                )
            )
            await db.commit()

            org3 = Organization(
                name='ООО "Стройматериалы"', building_id=buildings[2].id
            )
            db.add(org3)
            await db.commit()
            await db.refresh(org3)

            phone3_1 = PhoneNumber(number="4-444-444", organization_id=org3.id)
            db.add(phone3_1)
            await db.commit()

            await db.execute(
                organization_activity.insert().values(
                    [
                        {"organization_id": org3.id, "activity_id": construction.id},
                        {"organization_id": org3.id, "activity_id": materials.id},
                        {"organization_id": org3.id, "activity_id": cement.id},
                    ]
                )
            )
            await db.commit()

            org4 = Organization(name='ИП "Молочная ферма"', building_id=buildings[2].id)
            db.add(org4)
            await db.commit()
            await db.refresh(org4)

            phone4_1 = PhoneNumber(number="5-555-555", organization_id=org4.id)
            phone4_2 = PhoneNumber(number="9-999-999", organization_id=org4.id)
            db.add_all([phone4_1, phone4_2])
            await db.commit()

            await db.execute(
                organization_activity.insert().values(
                    [
                        {"organization_id": org4.id, "activity_id": food.id},
                        {"organization_id": org4.id, "activity_id": dairy_products.id},
                        {"organization_id": org4.id, "activity_id": milk.id},
                        {"organization_id": org4.id, "activity_id": cheese.id},
                    ]
                )
            )
            await db.commit()

            org5 = Organization(name='ООО "Техносервис"', building_id=buildings[3].id)
            db.add(org5)
            await db.commit()
            await db.refresh(org5)

            phone5_1 = PhoneNumber(number="6-666-666", organization_id=org5.id)
            db.add(phone5_1)
            await db.commit()

            await db.execute(
                organization_activity.insert().values(
                    [
                        {"organization_id": org5.id, "activity_id": it.id},
                        {"organization_id": org5.id, "activity_id": software.id},
                        {"organization_id": org5.id, "activity_id": hardware.id},
                    ]
                )
            )
            await db.commit()

            org6 = Organization(name='ЗАО "Мясокомбинат"', building_id=buildings[4].id)
            db.add(org6)
            await db.commit()
            await db.refresh(org6)

            phone6_1 = PhoneNumber(number="1-111-111", organization_id=org6.id)
            phone6_2 = PhoneNumber(number="8-912-345-67-89", organization_id=org6.id)
            db.add_all([phone6_1, phone6_2])
            await db.commit()

            await db.execute(
                organization_activity.insert().values(
                    [
                        {"organization_id": org6.id, "activity_id": food.id},
                        {"organization_id": org6.id, "activity_id": meat_products.id},
                        {"organization_id": org6.id, "activity_id": beef.id},
                        {"organization_id": org6.id, "activity_id": pork.id},
                    ]
                )
            )
            await db.commit()

            logger.info("Organizations created successfully")
            logger.info("Database initialized successfully with test data")

        except Exception as e:
            await db.rollback()
            logger.error(f"Error initializing database: {e}")
            raise


if __name__ == "__main__":
    import asyncio

    asyncio.run(init_db())
