# -*- coding: utf-8 -*-
from collective.messagesviewlet import _
from plone import api
from plone.indexer.wrapper import IndexableObjectWrapper
from plone.registry import field, Record
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

import logging


logger = logging.getLogger("collective.messagesviewlet: upgrade. ")


def upgrade_to_1001(context):
    """ Avoid warning about unresolved dependencies """
    setup = api.portal.get_tool("portal_setup")
    registry = setup.getImportStepRegistry()
    config = {
        "collective-messagesviewlet-post-install": (
            u"browserlayer",
            u"controlpanel",
            u"cssregistry",
            u"propertiestool",
            u"rolemap",
            u"typeinfo",
            u"workflow",
        ),
        "collective-messagesviewlet-messages": (),
    }
    for key, value in config.items():
        step = registry._registered.get(key)
        if step is not None:
            step["dependencies"] = value
    setup._p_changed = True
    logger.info("Import step dependency corrected")


def upgrade_to_2000(context):
    """
        Add timezone to start and end
    """
    catalog = api.portal.get_tool("portal_catalog")
    brains = catalog(portal_type="Message")
    logger.info("Found {0} messages".format(len(brains)))
    count = 0
    for brain in brains:
        obj = brain.getObject()
        correction = False
        for attr in ("start", "end"):
            if getattr(obj, attr, False):
                # use plone.indexer index to be sure we have same value
                indexable_wrapper = IndexableObjectWrapper(obj, catalog)
                setattr(obj, attr, getattr(indexable_wrapper, attr))
                correction = True
        if correction:
            count += 1
        # reindex entire object to avoid datetime with/without TZ comparison
        # that breaks metadata update
        obj.reindexObject()
    logger.info("Corrected {0} messages".format(count))


def add_authorize_local_message_to_registry(context):
    portal_setup = api.portal.get_tool("portal_setup")
    portal_setup.runAllImportStepsFromProfile(
        "profile-collective.messagesviewlet:default"
    )
    registry = getUtility(IRegistry)
    records = registry.records
    if (
        "messagesviewlet.authorize_local_message"
        in records
    ):  # noqa
        return

    logger.info(
        "Adding collective.messagesviewlet.browser.controlpanel.IMessagesviewletSettings.authorize_local_message to registry"  # noqa
    )  # noqa
    record = Record(
        field.Bool(
            title=_(u"Authorize local message"),
            description=_(
                u"Local message should be stored in folderish. Can be print just on this folderish item or on the folderish and these children"  # noqa
            ),
            required=False,
            default=False,
        ),
        value=False,
    )
    records[
        "messagesviewlet.authorize_local_message"
    ] = record  # noqa
