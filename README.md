# Euromillions (UK only)

A little script that automatically plays euromillions for you, as long as there is enough balance on the account.

### How to

1. Rename `config.example.json` to `config.json`
2. Fill in the required fields in there
3. Run `python start.py`

## Configurations

**Please note, this script requires Python 3**

In order for the script to work, `config.json` needs a few fields to be filled in.

1. **username**. This is your euromillions username.
2. **password**. Your euromillions password.
3. **strategy**
   * **all**. This will buy 3 tickets: 1 - statistical, taking the most frequent numbers in the previous winning tickets. 2 - a random ticket. 3 - numbers of your choosing (configured in **_fixed_ticket_**).
   * **statistical**. This will only play statistical numbers.
   * **random**. Only random numbers.
   * **fixed**. Only fixed numbers.
4. **fixed_ticket**. This is where you fill in your fixed ticket numbers. Please note that the ticket array length needs to be 7 (5 normal numbers, 2 lucky numbers). _i.e. [1, 2, 3, 4, 5, 6, 7]_
5. **number_weeks**. Number of weeks these tickets should recur.

Example config file:

```
{
    "username": "Pennywise",
    "password": "123",
    "strategy": "fixed",
    "fixed_ticket": [1, 2, 3, 4, 5],
    "number_weeks": 1
}
```

## Requirements

`BeatifulSoup` with `lxml`, `requests`.

### Tips

You can create a cron job, that runs every X day and the script will automatically calculate the earliest draw date (Tuesday or Friday).

**P.S. This is just for fun. There is never, ever a guarantee that you will ever win anything in lottery. Odds will always remain the same, no matter what.**
