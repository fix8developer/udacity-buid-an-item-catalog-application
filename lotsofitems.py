from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Categories, Base, Items, User

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# -------------------------------------------------------------------------
# Create dummy user
# -------------------------------------------------------------------------
# -----------------------
# User number 1
# -----------------------
user1 = User(
    name="Waqar Iqbal", email="kashif@udacity.com",
    picture="""https://en.wikipedia.org/wiki/Kashif_(1983_album)#/media/File:
        Kashif_1983.jpg
    """
)
session.add(user1)
session.commit()


# -------------------------------------------------------------------------
# Create dummy categories
# -------------------------------------------------------------------------
# -----------------------
# Catagory number 1
# -----------------------
categories1 = Categories(
    user_id=1, name="Android"
)
session.add(categories1)
session.commit()

# -----------------------
# Catagory number 2
# -----------------------
categories2 = Categories(
    user_id=1, name="Apple"
)
session.add(categories2)
session.commit()

# -----------------------
# Catagory number 3
# -----------------------
categories3 = Categories(
    user_id=1, name="Windows"
)
session.add(categories3)
session.commit()


# -------------------------------------------------------------------------
# Create dummy Items
# -------------------------------------------------------------------------
# -----------------------
# Item number 1
# -----------------------
itme1 = Items(
    name="Htc One M9", description="""
        The HTC One M9 is an Android smartphone manufactured and marketed by
        HTC. The third-generation One was officially unveiled in a press
        conference at Mobile World Congress on March 1, 2015 and it was
        released to wide retail availability on April 10, 2015. It is the
        successor to HTC One
    """,
    categories=categories1, user_id=1)
session.add(itme1)
session.commit()

# -----------------------
# Item number 2
# -----------------------
itme2 = Items(
    name="Samsung Note 8", description="""
        The Note 8 is powered by an Exynos 8895 or Snapdragon 835 processor,
        depending on geographic region, along with 6 GB of RAM. ... It has
        support for Samsung DeX as well, letting Note 8 users connect their
        device to a dock and monitor to enable a PC-like computing environment
        with mouse and keyboard input.
    """,
    categories=categories1, user_id=1)
session.add(itme2)
session.commit()

# -----------------------
# Item number 3
# -----------------------
itme3 = Items(
    name="LG G6", description="""
        LG G6 comes with 4GB of RAM. The phone packs 32GB of internal storage
        that can be expanded up to 2000GB via a microSD card. As far as the
        cameras areconcerned, the LG G6 packs a 13-megapixel primary camera on
        the rear and a 5-megapixel front shooter for selfies. The LG G6 is
        powered by a 3300mAh non removable battery.
    """,
    categories=categories1, user_id=1)
session.add(itme3)
session.commit()

# -----------------------
# Item number 4
# -----------------------
itme4 = Items(
    name="iPhone 6", description="""
        Apple iPhone 6 smartphone was launched in September 2014. The phone
        comes with a 4.70-inch touchscreen display with a resolution of 750
        pixels by 1334 pixels at a PPI of 326 pixels per inch. Apple iPhone 6
        price in Pakistan starts from Rs. 19,340. Apple iPhone 6 comes with 1GB
        of RAM.
    """,
    categories=categories2, user_id=1)
session.add(itme4)
session.commit()

# -----------------------
# Item number 5
# -----------------------
itme5 = Items(
    name="Nokia Lumia 630", description="""
        The Nokia Lumia 630 (Orange, Dual SIM) supports the Windows v8.1
        operating system along with 1.2GHz Snapdragon 400 quad core processor.
        This Windows phone is backed by a 512MB RAM and 8GB internal memory
        which is expandable up to 128GB.
    """,
    categories=categories3, user_id=1)
session.add(itme5)
session.commit()

# -----------------------
# Item number 6
# -----------------------
itme6 = Items(
    name="Nokia Lumia 530", description="""
        Nokia Lumia 530 Dual SIM Brief Description. Nokia Lumia 530 Dual SIM is
        a dual sim (GSM+GSM) with dual-standby smartphone. It has a 4-inch TFT
        capacitative display and has a 1.2 GHz quad-core processor coupled with
        512 MB RAM.
    """,
    categories=categories3, user_id=1)
session.add(itme6)
session.commit()

# -----------------------
# Item number 7
# -----------------------
itme7 = Items(
    name="iPad 4", description="""
        Officially called the "iPad with Retina Display" by Apple, the iPad 4
        is a fairly minor update over the third generation iPad, offering the
        same 9.7-inch Retina display screen, weight and battery life as the
        previous iPad.
    """,
    categories=categories2, user_id=1)
session.add(itme7)
session.commit()


print "added menu items!"
