# Mit Affald - Aalborg

Support for schedules provided by [Aalborg Kommune - Mit Affald](https://aalborg.renoweb.dk/Legacy/selvbetjening/mit_affald.aspx), serving Aalborg Municipality, Denmark.

## Configuration via configuration.yaml

```yaml
waste_collection_schedule:
    sources:
    - name: aalborg_renoweb_dk
      args:
        address: ADDRESS
```

### Configuration Variables

**address**
*(String) (required)*

## Example

```yaml
waste_collection_schedule:
    sources:
    - name: aalborg_renoweb_dk
      args:
        address: Generiskvej 42, 9000 Aalborg
```

## How to get the source argument

Using your street name and number followed by postal code and city
should be fine. Otherwise search for your address here [Aalborg Kommune - Mit Affald](https://aalborg.renoweb.dk/Legacy/selvbetjening/mit_affald.aspx)
And enter the full string including the parenthesis with "Ejd.nr" and "BFE.nr.".
