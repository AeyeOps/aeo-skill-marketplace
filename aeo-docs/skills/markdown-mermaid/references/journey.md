# User Journey Diagrams

**Keyword:** `journey`

**Purpose:** Visualize user workflows and satisfaction levels.

## Basic Syntax

```mermaid
journey
    title User Journey
    section Section Name
        Task 1: 5: Actor1, Actor2
        Task 2: 3: Actor1
```

## Task Syntax

```
Task name: score: actor1, actor2, actor3
```

**Score:** 1-5 (inclusive)
- 1: Very dissatisfied
- 5: Very satisfied

## Example

```mermaid
journey
    title Online Shopping Experience
    section Browse
        Search products: 5: Customer
        View details: 4: Customer
    section Purchase
        Add to cart: 4: Customer
        Checkout: 3: Customer, System
        Payment: 2: Customer, PaymentGateway
    section Delivery
        Track order: 4: Customer, System
        Receive package: 5: Customer
```

## Key Limitations
- Score must be 1-5
- Limited formatting options
- Multiple actors separated by commas

## When to Use
- UX research documentation
- Customer journey mapping
- Process improvement analysis
- User story illustration
