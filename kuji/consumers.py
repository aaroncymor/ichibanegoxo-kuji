import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import KujiSession
from .services import initialize_draw, claim_prizes, summarize_kuji_session


class KujiSessionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.kuji_session_id = self.scope["url_route"]["kwargs"]["session_id"]

        print("KUJI_SESSION_ID", self.kuji_session_id)
        # Join a kuji session group
        self.group_name = f"kuji_session_{self.kuji_session_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the kuji session group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        # TODO: submits user id for random raffle generation
        # HTMX sends data as a standard JSON string payload
        data = json.loads(text_data)
        print("DATA", data)
        body = data.get("body", {})
        try:
            draw_count = int(body.get("draw_count", 0))
        except (ValueError, TypeError):
            draw_count = 0
        user_id = body.get("user_id", None)

        # # Render a snippet of pure HTML with new data
        kuji_session = await KujiSession.objects.aget(id=self.kuji_session_id)

        try:
            drawn_prizes = await sync_to_async(initialize_draw)(kuji_session, draw_count, user_id)
        except ValueError:
            print("ERROR: Not enough unclaimed raffles to draw")
            return

        claimed, error = await sync_to_async(claim_prizes)(drawn_prizes, user_id)
        if not claimed:
            print("ERROR: Failed to claim raffles", error)
            return

        summary = await sync_to_async(summarize_kuji_session)(kuji_session)

        print("DRAWN_PRIZES", drawn_prizes)
        print("CLAIMED", claimed)

        # Broadcast the message event out to everyone in the group
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "broadcast_message",
                "draw_count": draw_count,
                "user_id": user_id,
                "drawn_prizes": drawn_prizes,
                "summary": summary,
                "error": error
            }
        )

    async def broadcast_message(self, event):
        html_payload = f"""
        <span id="unclaimed-total" hx-swap-oob="innerHTML">{event["summary"]["unclaimed_total"]}</span>
        """
        
        raffles_summary_html = "<ul id='raffles-summary' hx-swap-oob='innerHTML'>"
        for raffle in event["summary"]["raffles"]:
            raffles_summary_html += f"<li>[{raffle['tier']}] - {raffle['name']} (Unclaimed: {raffle['unclaimed_count']})</li>"
        raffles_summary_html += "</ul>"
        
        drawn_prizes_html = "<ul id='draw-results' hx-swap-oob='beforeend'>"
        for prize in event["drawn_prizes"]:
            drawn_prizes_html += f"<li>[{prize['tier']}] - {prize['name']}</li>"
        drawn_prizes_html += "</ul>"
        
        html_payload += raffles_summary_html
        html_payload += drawn_prizes_html
        
        # send raw HTML back out to the browser
        await self.send(text_data=html_payload)