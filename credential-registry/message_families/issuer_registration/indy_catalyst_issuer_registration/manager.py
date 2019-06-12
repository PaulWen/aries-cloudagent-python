"""Classes to manage issuer registrations."""

import asyncio
import logging

from indy_catalyst_agent.error import BaseError

# from indy_catalyst_agent.messaging.decorators.thread_decorator import ThreadDecorator

from indy_catalyst_agent.messaging.request_context import RequestContext
from indy_catalyst_agent.messaging.util import send_webhook

from .models.issuer_registration_state import IssuerRegistrationState
from .messages.register import IssuerRegistration


class IssuerRegistrationManagerError(BaseError):
    """Issuer registration error."""


class IssuerRegistrationManager:
    """Class for managing issuer registrations."""

    def __init__(self, context: RequestContext):
        """
        Initialize a IssuerRegistrationManager.

        Args:
            context: The context for this issuer registration
        """
        self._context = context
        self._logger = logging.getLogger(__name__)

    @property
    def context(self) -> RequestContext:
        """
        Accessor for the current request context.

        Returns:
            The request context for this connection

        """
        return self._context

    async def prepare_send(self, connection_id, issuer_registration):
        """
        Create an issuer registration state object and agent messages.

        Args:
            connection_id: Connection to send the issuer registration to
            issuer_registration: The issuer registration payload

        Returns:
            A tuple (
                issuer_registration_state,
                issuer_registration_message
            )

        """

        issuer_registration_state = IssuerRegistrationState(
            connection_id=connection_id,
            initiator=IssuerRegistrationState.INITIATOR_SELF,
            state=IssuerRegistrationState.STATE_REGISTRATION_SENT,
            issuer_registration=issuer_registration,
        )
        await issuer_registration_state.save(self.context)

        asyncio.ensure_future(
            send_webhook("issuer_registration", issuer_registration_state.serialize())
        )

        issuer_registration = IssuerRegistration(
            issuer_registration=issuer_registration
        )

        return issuer_registration_state, issuer_registration
