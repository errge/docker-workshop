# Bigger apps in Docker
So far we only used single containers, but microservice apps nowadays
need a lot of apps working together.

For example zulip needs all of this to function:

  - postgres
  - memcached
  - redis
  - rabbitmq
  - zulip itself

Maintaining, and starting up all of this is a lot of work, and with
big docker installations easy to lose track which rabbitmq belongs to
which app.

With docker compose, we can hold together all the parts of an
installation like this.

## Compose example
```
git clone https://github.com/zulip/docker-zulip.git
```

And look at `docker-compose.yml`

## Configure it
Register gitlab app at: https://gitlab.inf.ethz.ch/oauth/applications

- Ports to `80xx`
- `SETTING_EXTERNAL_HOST` to `<IP>:8443`
- `ZULIP_AUTH_BACKENDS` to `GitLabAuthBackend`
- `SETTING_SOCIAL_AUTH_GITLAB_KEY` to gitlab api key
- `SECRETS_social_auth_gitlab_secret` to gitlab api secret
- `SETTING_SOCIAL_AUTH_GITLAB_API_URL` to `https://gitlab.inf.ethz.ch`

Start with: `docker compose up`

Get realm creation URL with: `docker compose exec -u zulip zulip  /home/zulip/deployments/current/manage.py generate_realm_creation_link`

## Let's play with it
Try this out together and see how it goes.

## Cleanup

`docker compose rm` + `docker compose down -v`
