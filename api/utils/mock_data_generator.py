import asyncio

from sqlmodel import Session

from api.database import engine
from api.public.user.models import User
from api.public.listing.models import Listing
from api.public.listing_picture.models import ListingPicture
from api.public.user_info.models import UserInfo
from api.utils.logger import logger_config

logger = logger_config(__name__)

import contextlib

from api.database import get_session
from api.auth import get_user_db, get_user_manager
from api.public.user.models import UserCreate
from fastapi_users.exceptions import UserAlreadyExists

get_session_context = contextlib.contextmanager(get_session)
get_user_db_context = contextlib.contextmanager(get_user_db)
get_user_manager_context = contextlib.contextmanager(get_user_manager)


async def create_user(email: str, password: str, is_superuser: bool = False, is_accepted: bool = False) -> User:
    try:
        with get_session_context() as session:
            with get_user_db_context(session) as user_db:
                with get_user_manager_context(user_db) as user_manager:
                    user = await user_manager.create(
                        UserCreate(
                            email=email, password=password, is_superuser=is_superuser, is_accepted=is_accepted
                        )
                    )
                    print(f"User created {user}")
                    return user
    except UserAlreadyExists:
        print(f"User {email} already exists")



async def create_user_and_listings(): #TODO
    with Session(engine) as session:
        try:
            superuser = await create_user('super@user.com', 'password', is_superuser=True,
                                          is_accepted=True)
            user_1 = await create_user('john@doe.com', 'password', is_accepted=True)
            session.add(superuser)
            session.add(user_1)
            session.commit()
            session.refresh(user_1)
            session.refresh(superuser)

            userinfo = UserInfo(user_id=user_1.id,
                                full_name="John Doe",
                                tg_id=12312312,  # Generating random 6 digit number
                                user=user_1,
                                telegram='@johndoe',
                                whatsapp='+12345678901',
                                instagram='@johndoe',
                                linkedin='linkedin.com/in/johndoe',
                                description='''John Doe is a software engineer with over 10 years of experience in the industry.
He specializes in backend development, data analysis, and AI. He is open for collaborations and you can connect with him on his social media profiles. His favourite hobbies are photography and hiking.
                                ''',
                                picture_url='https://fscommunity.s3.eu-west-1.amazonaws.com/7_1711145418585000_0.jpeg',
                                where_to_rent='New York, USA',
                                where_to_let='San Francisco, USA',
                                meet=True,
                                notifications=True,
                                contact_email='john@doe.com'
                                )

            session.add(userinfo)
            session.commit()


            listing_1 = Listing(date_from='2024-01-01T12:00:00.00+00:00',
                                date_to='2024-01-01T12:00:00.00+00:00',
                                country='Germany',
                                city='Munich',
                                user_id=user_1.id,
                                user=user_1,
                                description='''Modern and cozy apartment in the heart of the city. 
Fully furnished, with all necessary amenities (WiFi, TV, washing machine, etc.). 
Great for short-term stays, business trips, and family vacations. No smoking and no pets.''',
                                price='$1500',
                                comments='Very convenient location. Close to the subway and multiple grocery stores. Great view from the balcony.',
                                status='POSTED'
                                )

            listing_2 = Listing(date_from='2024-01-01T12:00:00.00+00:00',
                                date_to='2024-01-01T12:00:00.00+00:00',
                                country='Germany',
                                city='Munich',
                                user_id=user_1.id,
                                user=user_1,
                                description='''Modern and cozy apartment in the heart of the city. 
Fully furnished, with all necessary amenities (WiFi, TV, washing machine, etc.). 
Great for short-term stays, business trips, and family vacations. No smoking and no pets.''',
                                price='$1500',
                                comments='Very convenient location. Close to the subway and multiple grocery stores. Great view from the balcony.',
                                status='POSTED'
                                )

            listing_3 = Listing(date_from='2024-01-01T12:00:00.00+00:00',
                                date_to='2024-01-01T12:00:00.00+00:00',
                                country='Germany',
                                city='Munich',
                                user_id=user_1.id,
                                user=user_1,
                                description='''Modern and cozy apartment in the heart of the city. 
Fully furnished, with all necessary amenities (WiFi, TV, washing machine, etc.). 
Great for short-term stays, business trips, and family vacations. No smoking and no pets.''',
                                price='$1500',
                                comments='Very convenient location. Close to the subway and multiple grocery stores. Great view from the balcony.',
                                status='POSTED'
                                )

            session.add(listing_1)
            session.add(listing_2)
            session.add(listing_3)
            session.commit()
            session.refresh(listing_1)
            session.refresh(listing_2)
            session.refresh(listing_3)

            urls = [
                "https://fscommunity.s3.eu-west-1.amazonaws.com/12_1711230873321000_0.jpeg",
                "https://fscommunity.s3.eu-west-1.amazonaws.com/12_1711230873321000_1.jpeg",
                "https://fscommunity.s3.eu-west-1.amazonaws.com/12_1711230873321000_2.jpeg",
                "https://fscommunity.s3.eu-west-1.amazonaws.com/12_1711230873322000_3.jpeg",
                "https://fscommunity.s3.eu-west-1.amazonaws.com/12_1711230873322000_4.jpeg",
                "https://fscommunity.s3.eu-west-1.amazonaws.com/12_1711230873322000_5.jpeg"
            ]
            for listing in [listing_1, listing_2, listing_3]:
                for url in urls:
                    picture = ListingPicture(
                        picture_url=url,
                        listing=listing,
                        listing_id=listing.listing_id
                    )
                    session.add(picture)
            session.commit()



            logger.info("=========== MOCK DATA CREATED ===========")
            logger.info("User %s", user_1)
            logger.info("User listings %s", user_1.listings)
            logger.info("Listing %s", listing_1)
            logger.info("listing_1 pictures %s", listing_1.listing_pictures)
            logger.info("===========================================")
        except Exception as e:
            print(f'Seems mock data is already there. {e}')
