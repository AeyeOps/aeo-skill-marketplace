# Sequence Diagrams

D2's sequence diagrams use `shape: sequence_diagram` on a container. Inside, every connection is a message between actors, drawn in declaration order with vertical lifelines.

**Critical rule**: Inside a `sequence_diagram` container, scoping is FLAT — every actor (or message) referenced anywhere inside the container is resolved against the diagram root. So actors used in nested groups must be predeclared at the diagram's top level if D2 doesn't see them in time.

## Hello-world

```d2
shape: sequence_diagram

alice -> bob: Hello
bob -> alice: Hi back
```

That's it. Actor lanes are inferred from the connections.

## Putting it inside a container

```d2
auth flow: {
  shape: sequence_diagram

  user -> client: tap login
  client -> auth-server: POST /authorize
  auth-server -> user: redirect to login UI
  user -> auth-server: enter credentials
  auth-server -> client: redirect with code
  client -> auth-server: POST /token (code)
  auth-server -> client: access_token
}
```

The container can have its own label, theme, etc. — only the `sequence_diagram` shape changes the layout rules inside.

## Actor types — pick the right shape

By default, actors are rectangles. Override per-actor for visual variety:

```d2
shape: sequence_diagram

alice: { shape: person }
bob:   { shape: person }
db:    { shape: cylinder }
queue: { shape: queue }

alice -> bob: chat
bob -> queue: enqueue
queue -> db: persist
```

Common actor shapes for sequence diagrams: `person`, `cylinder` (DB), `queue`, `package`, `cloud`, `class`, `code`.

## Message types

### Synchronous (default)

```d2
client -> server: GET /users
```

### Asynchronous (dashed line)

```d2
client -> server: notify {
  style.stroke-dash: 5
}
```

### Return / response

```d2
server -> client: 200 OK {
  style.stroke-dash: 3
}
```

### Self-message

```d2
shape: sequence_diagram

server -> server: validate
server -> server: update cache
```

A self-message draws a small loop on the actor's lifeline.

### Bidirectional / undirected

```d2
client <-> server: handshake     # arrowheads on both ends
client -- server: opaque link    # no arrowheads (rare in sequences)
```

## Activations / spans (vertical activity bars)

To show "actor B is processing during this span", use a nested key on the actor — that key becomes a span/activation rectangle on the lifeline:

```d2
shape: sequence_diagram

alice -> bob.active: request
bob.active -> bob.active: validate
bob.active -> charlie.processing: forward
charlie.processing -> bob.active: result
bob.active -> alice: response
```

Each `actor.span-name` creates a span on `actor`'s lifeline. The span lives for the duration of all messages that use it.

Nested spans:

```d2
shape: sequence_diagram

a -> b.outer: start
b.outer -> b.outer.inner: nested begin
b.outer.inner -> a: partial
b.outer -> a: done
```

## Notes

A "note" is just a child shape on an actor (no connections to/from it). It renders as a parchment-like sticker:

```d2
shape: sequence_diagram

alice -> bob: hi
bob.note: |md
  Bob is offline,
  message goes to retry queue
|
bob -> alice: ack
```

## Groups (alt / opt / par / loop)

**There is no `alt`/`opt`/`par`/`loop` keyword.** D2 implements them as **plain nested containers** whose key happens to be named that way. The convention:

- `alt` = mutually exclusive branches (if/else)
- `opt` = optional branch (if without else)
- `par` = parallel branches
- `loop` = repeated until exit condition

```d2
shape: sequence_diagram

# Predeclare actors used in groups (FLAT SCOPING — required)
alice
bob
charlie

alice -> bob: query

alt: {
  alice -> bob: cache hit {
    bob -> alice: cached value
  }
  alice -> bob: cache miss {
    bob -> charlie: fetch
    charlie -> bob: data
    bob -> alice: data
  }
}

opt: {
  alice -> bob: notify on success
}

loop: {
  alice -> bob: poll
  bob -> alice: status
}

par: {
  alice -> charlie: log {
    style.stroke-dash: 5
  }
  alice -> bob: continue
}
```

You can name the group with a label for clarity:

```d2
shape: sequence_diagram

retry-loop: {
  client -> server: request
  server -> client: 503
  client -> server: retry
}
```

## Message numbering (manual)

D2 doesn't auto-number; if you want numbers, prefix labels:

```d2
shape: sequence_diagram

a -> b: 1. begin
b -> c: 2. forward
c -> b: 3. ack
b -> a: 4. done
```

## Ordering control

Messages render in **declaration order**. To re-order, move the lines. There's no `order:` attribute.

```d2
shape: sequence_diagram

# This sequence runs top-to-bottom
client -> server: GET /a
client -> server: GET /b      # second
client -> server: GET /c      # third
```

## Lifeline styling

Style the actor itself and the lifeline inherits:

```d2
shape: sequence_diagram

alice: { style.fill: lavender }
bob: {
  shape: person
  style.fill: lightyellow
}

alice -> bob: hi
```

Style spans:

```d2
shape: sequence_diagram

bob.active: {
  style.fill: "#a5d6a7"
  style.stroke: green
}

alice -> bob.active: request
bob.active -> alice: response
```

## Direction

Sequence diagrams are always vertical (time goes down). Setting `direction:` inside a `sequence_diagram` container has no effect on the lifeline orientation.

## A complete realistic example

```d2
OAuth 2 Authorization Code Flow: {
  shape: sequence_diagram

  user: { shape: person }
  app
  authz
  resource

  user -> app: click "login"
  app -> authz: GET /authorize?client_id=...&redirect_uri=...

  alt: {
    happy: {
      authz -> user: render login form
      user -> authz: submit credentials
      authz -> app: 302 with auth code {
        style.stroke-dash: 3
      }
      app -> authz: POST /token (code, secret)
      authz -> app: access_token + refresh_token

      loop: {
        app -> resource: GET /api with access_token
        resource -> app: 200 + data
      }
    }
    refresh: {
      app -> authz: POST /token (refresh_token)
      authz -> app: new access_token
    }
  }

  opt: {
    user -> app: logout
    app -> authz: revoke token
  }
}
```

## Common pitfalls

1. **Actors used in nested groups must be predeclared at the top level of the sequence_diagram container.** D2 won't always autodiscover them through the flat scoping in time.
2. **`alt`/`opt`/`par`/`loop` are not keywords — they're container names by convention.** They produce the bracketed-group rendering automatically because they're nested containers inside a `sequence_diagram`. If you call them `myalt:` they still render as a group, just without the alt convention.
3. **Spans (`actor.span`) use dot notation, not new actor declarations.** `bob.active` is bob's span, not a new actor named `bob.active`.
4. **There's no auto-numbering of messages.** Add numbers to the label text manually if you need them.
5. **`direction:` doesn't change orientation.** It's always vertical.
6. **Notes are shapes with no connections** — declare them with a label and they appear as stickies on the lifeline.

## Cheat sheet

```text
shape: sequence_diagram          declare in a container

a -> b: msg                      sync message
a -> b: msg { style.stroke-dash: 5 }   async/return
a -> a: thinking                 self-message
a <-> b: handshake               bidirectional

a.span -> b.span: ...            activations / spans
a.note: text                     sticky note on a's lifeline

alt: { branch1: { ... } branch2: { ... } }   alt fragment
opt: { ... }                                  optional fragment
par: { ... }                                  parallel
loop: { ... }                                 loop
```
