import singer
from singer import utils
from singer.catalog import Catalog, write_catalog
from tap_quickbooks.discover import do_discover
from tap_quickbooks.client import QuickbooksClient
from tap_quickbooks.sync import do_sync


LOGGER = singer.get_logger()


@utils.handle_top_exception(LOGGER)
def main():
    required_config_keys = ['start_date', 'user_agent', 'realm_id', 'client_id', 'client_secret', 'refresh_token']
    args = singer.parse_args(required_config_keys)

    config = args.config
    if args.dev:
        LOGGER.warning("Executing Tap in Dev mode")

    state = args.state

    if state and 'latest_refresh_token' in state:
        config.update({'refresh_token': state['latest_refresh_token']})
        LOGGER.info('Loading latest_refresh_token from state to config')

    client = QuickbooksClient(args.config_path, config, args.dev)

    if args.properties and not args.catalog:
        raise Exception("DEPRECATED: Use of the 'properties' parameter is not supported. Please use --catalog instead")

    if args.discover:
        LOGGER.info("Starting discovery mode")
        catalog = do_discover()
        write_catalog(catalog)
        LOGGER.info("Finished discovery mode")
    else:
        if args.catalog:
            catalog = args.catalog
        else:
            catalog = do_discover()

        LOGGER.info("Starting sync mode")
        do_sync(client, config, state, catalog)
        LOGGER.info("Finished sync mode")

if __name__ == "__main__":
    main()
