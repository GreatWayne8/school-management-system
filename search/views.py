from itertools import chain
from django.views.generic import ListView
from core.models import NewsAndEvents
from course.models import Program, Course
from quiz.models import Quiz


class SearchView(ListView):
    template_name = "search/search_view.html"
    paginate_by = 20
    count = 0

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["count"] = self.count or 0
        context["query"] = self.request.GET.get("q")
        return context

    def get_queryset(self):
        request = self.request
        query = request.GET.get("q", None)

        if query:
            # Perform the searches on each model
            news_events_results = NewsAndEvents.objects.search(query)
            program_results = Program.objects.search(query)
            course_results = Course.objects.search(query)
            quiz_results = Quiz.objects.search(query)

            # Combine querysets
            combined_results = list(
                chain(news_events_results, program_results, course_results, quiz_results)
            )

            # Sort by primary key (assuming you want the latest results first)
            combined_results = sorted(combined_results, key=lambda instance: instance.pk, reverse=True)

            # Set the count for context
            self.count = len(combined_results)

            return combined_results
        
        # Return an empty queryset if no query is provided
        return NewsAndEvents.objects.none()
