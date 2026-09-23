import unittest
from contextlib import contextmanager

from flask import template_rendered

from app import create_app, db
from app.models import Accommodation, Destination


class TestConfig:
    TESTING = True
    SECRET_KEY = "phase2-test-key"
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


class Phase2RouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.jeju = Destination(
            name="제주",
            region="제주특별자치도",
            description="바다와 오름을 함께 즐기는 여행지",
            season="봄",
            purpose="자연",
            atmosphere="낭만적인",
            budget_level="보통",
            recommended_days=3,
        )
        self.gangneung = Destination(
            name="강릉",
            region="강원특별자치도",
            description="겨울 바다와 커피를 즐기는 여행지",
            season="겨울",
            purpose="휴양",
            atmosphere="조용한",
            budget_level="보통",
            recommended_days=2,
        )
        db.session.add_all((self.jeju, self.gangneung))
        db.session.flush()

        self.jeju_hotel = Accommodation(
            destination_id=self.jeju.id,
            name="제주 테스트 호텔",
            address="제주특별자치도 제주시",
            description="제주 테스트 숙소",
            price_per_night=100000,
            capacity=2,
            rating=4.5,
        )
        self.gangneung_hotel = Accommodation(
            destination_id=self.gangneung.id,
            name="강릉 테스트 호텔",
            address="강원특별자치도 강릉시",
            description="강릉 테스트 숙소",
            price_per_night=90000,
            capacity=3,
            rating=4.2,
        )
        db.session.add_all((self.jeju_hotel, self.gangneung_hotel))
        db.session.commit()

        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_context(self, path):
        with captured_templates(self.app) as templates:
            response = self.client.get(path)
        self.assertTrue(templates, f"Template이 렌더링되지 않았습니다: {path}")
        return response, templates[-1][0].name, templates[-1][1]

    def test_main_page_uses_database_destinations(self):
        response, template, context = self.get_context("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(template, "main/index.html")
        self.assertEqual(len(context["hero_slides"]), 4)
        self.assertEqual(
            context["hero_slides"][0]["filename"],
            "img/main/hero-jeju-sunset.png",
        )
        self.assertEqual(
            [item.name for item in context["popular_destinations"]],
            ["제주", "강릉"],
        )
        page = response.get_data(as_text=True)
        self.assertEqual(page.count('class="hero__slide"'), 4)
        self.assertEqual(page.count("data-hero-dot="), 4)
        self.assertIn('action="/destinations"', page)
        self.assertIn('name="keyword"', page)

    def test_destination_list(self):
        response, template, context = self.get_context("/destinations")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(template, "destination/list.html")
        self.assertEqual(len(context["destinations"]), 2)
        self.assertEqual(context["keyword"], "")

    def test_destination_keyword_search(self):
        response, _, context = self.get_context(
            "/destinations?keyword=%EB%B0%94%EB%8B%A4"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item.name for item in context["destinations"]],
            ["제주", "강릉"],
        )

    def test_destination_filters_individually(self):
        cases = {
            "region=%EC%A0%9C%EC%A3%BC%ED%8A%B9%EB%B3%84%EC%9E%90%EC%B9%98%EB%8F%84": "제주",
            "season=%EA%B2%A8%EC%9A%B8": "강릉",
            "purpose=%EC%9E%90%EC%97%B0": "제주",
            "atmosphere=%EC%A1%B0%EC%9A%A9%ED%95%9C": "강릉",
        }
        for query, expected_name in cases.items():
            with self.subTest(query=query):
                response, _, context = self.get_context(
                    f"/destinations?{query}"
                )
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    [item.name for item in context["destinations"]],
                    [expected_name],
                )

    def test_destination_filters_are_combined_with_and(self):
        response, _, context = self.get_context(
            "/destinations?season=%EB%B4%84&purpose=%EC%9E%90%EC%97%B0"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item.name for item in context["destinations"]],
            ["제주"],
        )

    def test_invalid_filter_returns_empty_result(self):
        response, _, context = self.get_context(
            "/destinations?season=NOT-A-SEASON"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(context["destinations"], [])

    def test_destination_detail_and_missing_destination(self):
        response, template, context = self.get_context(
            f"/destinations/{self.jeju.id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(template, "destination/detail.html")
        self.assertEqual(context["destination"].name, "제주")
        self.assertEqual(context["reviews"], [])
        self.assertEqual(
            [item.name for item in context["accommodations"]],
            ["제주 테스트 호텔"],
        )
        self.assertEqual(self.client.get("/destinations/9999").status_code, 404)

    def test_nearby_accommodations_are_scoped_to_destination(self):
        response, template, context = self.get_context(
            f"/destinations/{self.jeju.id}/accommodations"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(template, "accommodation/list.html")
        self.assertEqual(context["destination"].name, "제주")
        self.assertEqual(
            [item.name for item in context["accommodations"]],
            ["제주 테스트 호텔"],
        )
        page = response.get_data(as_text=True)
        self.assertIn("제주 주변 숙소", page)
        self.assertIn("제주 테스트 호텔", page)
        self.assertNotIn("강릉 테스트 호텔", page)
        self.assertIn("100,000원", page)
        self.assertIn("숙소 이미지 준비 중", page)

    def test_accommodation_list_and_detail(self):
        response, template, context = self.get_context("/accommodations")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(template, "accommodation/list.html")
        self.assertIsNone(context["destination"])
        self.assertEqual(len(context["accommodations"]), 2)
        list_page = response.get_data(as_text=True)
        self.assertIn("전체 숙소", list_page)
        self.assertIn("제주 테스트 호텔", list_page)
        self.assertIn("강릉 테스트 호텔", list_page)
        self.assertIn("최대 2명", list_page)

        response, template, context = self.get_context(
            f"/accommodations/{self.jeju_hotel.id}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(template, "accommodation/detail.html")
        self.assertEqual(context["accommodation"].name, "제주 테스트 호텔")
        self.assertEqual(context["accommodation"].destination.name, "제주")
        detail_page = response.get_data(as_text=True)
        self.assertIn("제주 테스트 숙소", detail_page)
        self.assertIn("제주 여행지 보기", detail_page)
        self.assertIn("예약 기능은 Phase 5에서 제공됩니다.", detail_page)
        self.assertNotIn("예약하기", detail_page)
        self.assertEqual(self.client.get("/accommodations/9999").status_code, 404)


class EmptyDatabaseRouteTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_empty_database_pages_do_not_fail(self):
        for path in ("/", "/destinations", "/accommodations"):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)

        accommodation_page = self.client.get("/accommodations").get_data(
            as_text=True
        )
        self.assertIn("표시할 숙소가 없습니다.", accommodation_page)


if __name__ == "__main__":
    unittest.main()
