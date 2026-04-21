# Testing Expert - Full Guide

## React Testing

### Component Testing

**React Testing Library:**

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { UserList } from './UserList';

describe('UserList', () => {
  it('should render users', () => {
    const users = [
      { id: '1', name: 'John', email: 'john@example.com' }
    ];

    render(<UserList users={users} />);

    expect(screen.getByText('John')).toBeInTheDocument();
    expect(screen.getByText('john@example.com')).toBeInTheDocument();
  });

  it('should handle user click', () => {
    const onUserClick = jest.fn();
    const users = [{ id: '1', name: 'John' }];

    render(<UserList users={users} onUserClick={onUserClick} />);

    fireEvent.click(screen.getByText('John'));
    expect(onUserClick).toHaveBeenCalledWith('1');
  });
});
```

**Testing Hooks:**

```typescript
import { renderHook, act } from '@testing-library/react';
import { useUsers } from './useUsers';

describe('useUsers', () => {
  it('should fetch users', async () => {
    const { result } = renderHook(() => useUsers());

    await act(async () => {
      await result.current.fetchUsers();
    });

    expect(result.current.users).toHaveLength(1);
    expect(result.current.loading).toBe(false);
  });
});
```

### Next.js Testing

**Page Testing:**

```typescript
import { render, screen } from '@testing-library/react';
import HomePage from '@/pages/index';

describe('HomePage', () => {
  it('should render page', () => {
    render(<HomePage />);
    expect(screen.getByRole('heading')).toBeInTheDocument();
  });
});
```

**API Route Testing:**

```typescript
import { createMocks } from 'node-mocks-http';
import handler from '@/pages/api/users';

describe('/api/users', () => {
  it('should return users', async () => {
    const { req, res } = createMocks({
      method: 'GET',
    });

    await handler(req, res);

    expect(res._getStatusCode()).toBe(200);
    const data = JSON.parse(res._getData());
    expect(data).toHaveProperty('users');
  });
});
```

## NestJS Testing

### Unit Tests

**Service Testing:**

```typescript
describe('UsersService', () => {
  let service: UsersService;
  let model: Model<User>;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        UsersService,
        {
          provide: getModelToken(User.name),
          useValue: mockUserModel,
        },
      ],
    }).compile();

    service = module.get<UsersService>(UsersService);
    model = module.get<Model<User>>(getModelToken(User.name));
  });

  it('should return users filtered by organization', async () => {
    const orgId = 'org1';
    const expectedUsers = [{ organization: orgId }];

    jest.spyOn(model, 'find').mockResolvedValue(expectedUsers as any);

    const result = await service.findAll(orgId);

    expect(result).toEqual(expectedUsers);
    expect(model.find).toHaveBeenCalledWith({
      organization: orgId,
      isDeleted: false
    });
  });
});
```

**Controller Testing:**

```typescript
describe('UsersController', () => {
  let controller: UsersController;
  let service: UsersService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [UsersController],
      providers: [
        {
          provide: UsersService,
          useValue: mockUsersService,
        },
      ],
    }).compile();

    controller = module.get<UsersController>(UsersController);
    service = module.get<UsersService>(UsersService);
  });

  it('should return users', async () => {
    const expectedUsers = [{ id: '1', email: 'test@example.com' }];
    jest.spyOn(service, 'findAll').mockResolvedValue(expectedUsers);

    const result = await controller.findAll('org1');

    expect(result).toEqual(expectedUsers);
  });
});
```

### Integration Tests

**Controller + Service + Database:**

```typescript
describe('UsersController Integration', () => {
  let app: INestApplication;
  let connection: Connection;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();

    connection = moduleFixture.get<Connection>(getConnectionToken());
  });

  afterAll(async () => {
    await connection.close();
    await app.close();
  });

  beforeEach(async () => {
    await User.deleteMany({});
  });

  it('should create and retrieve user', async () => {
    const createDto = { email: 'test@example.com', name: 'Test' };

    const createResponse = await request(app.getHttpServer())
      .post('/api/users')
      .send(createDto)
      .expect(201);

    const getResponse = await request(app.getHttpServer())
      .get(`/api/users/${createResponse.body._id}`)
      .expect(200);

    expect(getResponse.body.email).toBe(createDto.email);
  });
});
```

### E2E Tests

**Full Request/Response Cycle:**

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

    authToken = await getAuthToken();
  });

  afterAll(async () => {
    await app.close();
  });

  it('/api/users (GET)', () => {
    return request(app.getHttpServer())
      .get('/api/users')
      .set('Authorization', `Bearer ${authToken}`)
      .expect(200)
      .expect((res) => {
        expect(Array.isArray(res.body)).toBe(true);
      });
  });

  it('/api/users (POST)', () => {
    const createDto = { email: 'e2e@example.com', name: 'E2E Test' };

    return request(app.getHttpServer())
      .post('/api/users')
      .set('Authorization', `Bearer ${authToken}`)
      .send(createDto)
      .expect(201)
      .expect((res) => {
        expect(res.body.email).toBe(createDto.email);
      });
  });
});
```

## MongoDB Testing

### Test Database Setup

```typescript
beforeAll(async () => {
  await mongoose.connect(process.env.TEST_DB_URI);
});

afterAll(async () => {
  await mongoose.connection.close();
});

beforeEach(async () => {
  await User.deleteMany({});
});
```

### Data Seeding

```typescript
async function seedTestData() {
  await User.create([
    { email: 'user1@test.com', organization: 'org1' },
    { email: 'user2@test.com', organization: 'org1' },
    { email: 'user3@test.com', organization: 'org2' },
  ]);
}
```

### Mocking Database

```typescript
const mockUserModel = {
  find: jest.fn(),
  findOne: jest.fn(),
  create: jest.fn(),
  findByIdAndUpdate: jest.fn(),
  findByIdAndDelete: jest.fn(),
};

// In test
mockUserModel.find.mockResolvedValue([
  { _id: '1', email: 'test@example.com', organization: 'org1' }
]);
```

## Testing Best Practices

### 1. Test Isolation

- Each test should be independent
- Clean up after each test
- Use `beforeEach`/`afterEach` for setup/teardown
- Don't rely on test execution order

### 2. Meaningful Tests

- Test behavior, not implementation
- Use descriptive test names
- Test edge cases
- Test error cases

### 3. Mocking Strategy

- Mock external dependencies
- Mock database operations
- Mock API calls
- Don't mock what you're testing

### 4. Test Data

- Use factories for test data
- Keep test data minimal
- Use realistic data
- Clean up test data

### 5. Coverage

- Aim for high coverage
- Focus on critical paths
- Don't sacrifice quality for coverage
- Review coverage reports

## Common Testing Patterns

### Authentication Helper

```typescript
async function getAuthToken(organizationId = 'org1'): Promise<string> {
  const response = await request(app.getHttpServer())
    .post('/api/auth/login')
    .send({ email: 'test@example.com', password: 'test' });

  return response.body.accessToken;
}
```

### Request Helper

```typescript
function authenticatedRequest(method: string, url: string) {
  return async (token: string, body?: any) => {
    const req = request(app.getHttpServer())[method](url)
      .set('Authorization', `Bearer ${token}`);

    if (body) {
      req.send(body);
    }

    return req;
  };
}
```

### Test Fixtures

```typescript
export const userFixtures = {
  valid: {
    email: 'test@example.com',
    name: 'Test User',
    organization: 'org1'
  },
  invalid: {
    email: 'invalid-email',
    name: ''
  }
};
```

## Resources

- Jest Documentation: https://jestjs.io/
- React Testing Library: https://testing-library.com/react
- NestJS Testing: https://docs.nestjs.com/fundamentals/testing
- Testing Best Practices: https://kentcdodds.com/blog/common-mistakes-with-react-testing-library
