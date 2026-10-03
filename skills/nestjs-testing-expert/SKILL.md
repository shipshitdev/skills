---
name: nestjs-testing-expert
description: NestJS testing mechanics with Jest — building testing modules, mocking providers and repositories, writing service and controller specs, and driving HTTP end-to-end tests through the real application. Use for any test touching a NestJS service, controller, guard, module, or API endpoint, including test-module setup, provider overrides, database fakes, and Supertest request flows.
metadata:
  version: "2.2.2"
  tags: "nestjs, testing, jest, supertest, backend"
  author: Ship Shit Dev
when_to_use: "test a NestJS service, test a NestJS controller, Test.createTestingModule, createNestApplication, mock a NestJS provider, override a provider in tests, inject a repository mock, NestJS unit test, NestJS integration test, NestJS e2e test, supertest an API endpoint, test a guard or interceptor, spec file for a Nest module"
---

# NestJS Testing Expert

Build reliable Jest suites for NestJS modules, services, controllers, and HTTP
endpoints.

## Scope

This skill owns NestJS mechanics: testing modules, provider wiring, and
request-level end-to-end flows. For framework-agnostic questions — which level a
behavior belongs at, what a coverage number means, how to design a test that
survives refactoring, how to kill a flake — use `testing-expert`.

## When to Use

- Writing unit, integration, or end-to-end tests for a NestJS application
- Setting up a testing module, overriding providers, or faking a database
- Testing controllers, guards, interceptors, or pipes
- Exercising HTTP endpoints against a booted Nest application

## Levels in a Nest Application

- **Unit** — a service or provider in isolation, collaborators replaced with test
  doubles. No module graph beyond the providers under test.
- **Integration** — a module compiled with its real providers, external systems
  faked. Proves the wiring and the contracts between layers.
- **End-to-end** — a booted application driven over HTTP. Proves the full request
  path: pipes, guards, controller, service, persistence.

## Service Specs

Compile a testing module with the subject real and every collaborator supplied
explicitly. Injection tokens come from whatever integration provides them — an
ORM's token helper, a class reference, or a custom token constant.

```typescript
describe('UsersService', () => {
  let service: UsersService;
  let repository: jest.Mocked<UsersRepository>;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        UsersService,
        { provide: UsersRepository, useValue: createUsersRepositoryMock() },
      ],
    }).compile();

    service = module.get(UsersService);
    repository = module.get(UsersRepository);
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('returns only the active users of the requested organization', async () => {
    const expected = [{ id: '1', organization: 'org1' }];
    repository.find.mockResolvedValue(expected);

    const result = await service.findAll('org1');

    expect(result).toEqual(expected);
    expect(repository.find).toHaveBeenCalledWith({
      organization: 'org1',
      isDeleted: false,
    });
  });
});
```

Assert on the arguments the collaborator received when they encode a business
rule — the `isDeleted: false` filter above is the behavior, not an implementation
detail.

## Controller Specs

Register the controller, stub its service, and verify only the controller's own
job: argument extraction, delegation, and response shaping. Business rules belong
to the service spec.

```typescript
describe('UsersController', () => {
  let controller: UsersController;
  let service: jest.Mocked<UsersService>;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [UsersController],
      providers: [{ provide: UsersService, useValue: createUsersServiceMock() }],
    }).compile();

    controller = module.get(UsersController);
    service = module.get(UsersService);
  });

  it('passes the organization from the request through to the service', async () => {
    const expected = [{ id: '1', email: 'test@example.com' }];
    service.findAll.mockResolvedValue(expected);

    const result = await controller.findAll('org1');

    expect(result).toEqual(expected);
    expect(service.findAll).toHaveBeenCalledWith('org1');
  });
});
```

## Overriding Providers

Compile the real module and swap only what must not run for real.
`overrideProvider` and `overrideGuard` keep the rest of the graph authentic, so
the test still proves the wiring.

```typescript
const module: TestingModule = await Test.createTestingModule({
  imports: [UsersModule],
})
  .overrideProvider(MailerService)
  .useValue(mailerMock)
  .overrideGuard(AuthGuard)
  .useValue({ canActivate: () => true })
  .compile();
```

Override the guard only in tests about something else. Authorization itself
deserves end-to-end tests that run the real guard.

## Integration Tests

Boot the application, keep persistence real against a disposable database, and
reset state between tests.

```typescript
describe('Users (integration)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  beforeEach(async () => {
    await resetDatabase();
  });

  it('persists a created user and returns it on read', async () => {
    const created = await request(app.getHttpServer())
      .post('/api/users')
      .send({ email: 'test@example.com', name: 'Test' })
      .expect(201);

    const read = await request(app.getHttpServer())
      .get(`/api/users/${created.body.id}`)
      .expect(200);

    expect(read.body.email).toBe('test@example.com');
  });
});
```

Close the application in `afterAll`. A leaked Nest application holds its
connection pool open and hangs the Jest run.

## End-to-End Tests

Same boot, driven as a real client — authentication included.

```typescript
describe('Users API (e2e)', () => {
  let app: INestApplication;
  let authToken: string;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();

    authToken = await signInTestUser(app);
  });

  afterAll(async () => {
    await app.close();
  });

  it('rejects an unauthenticated list request', () =>
    request(app.getHttpServer()).get('/api/users').expect(401));

  it('returns the caller organization users when authenticated', () =>
    request(app.getHttpServer())
      .get('/api/users')
      .set('Authorization', `Bearer ${authToken}`)
      .expect(200)
      .expect((res) => {
        expect(Array.isArray(res.body)).toBe(true);
      }));
});
```

A shared `signInTestUser` helper keeps the token flow in one place and out of
every spec.

## Database Strategy

| Approach | Fits | Cost |
|---|---|---|
| Repository test double | Unit specs | Fastest; proves no SQL or schema |
| In-memory or embedded engine | Integration specs | Fast; behavior can drift from production |
| Disposable container per run | Integration and e2e specs | Slowest; highest fidelity |

Reset between tests by truncating or rolling back a transaction rather than
recreating the schema — schema rebuilds dominate suite runtime.

## Tips

- Give each spec its own module compilation; a shared one leaks state between tests.
- Reset mocks in `afterEach` so a stub set in one test cannot satisfy the next.
- Boot the application once per describe block and reset data per test — booting
  per test is the usual cause of a slow Nest suite.
- Keep tests deterministic: freeze the clock and pin the timezone rather than
  asserting on the real one.

## Checklist

- Clear arrange/act/assert structure
- Subject real, collaborators explicit — never the reverse
- Error and unauthorized paths covered, not just the happy path
- Application closed and mocks reset in teardown
- Fast to run
