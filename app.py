import streamlit as st
from Models.BlackScholes import *
from Datas.Option import *
from Models.MonteCarlo import *
from Datas.Market import *
from Models.BinomialTree import *
from Models.TrinomialTree import *
from Stats.Graphs import *
import time
from datetime import datetime, timedelta
from math import log10
import gc
from Stats.Greeks import *


st.markdown("""
<style>
    [data-testid="stSidebar"] {
        width: 110px !important;
    }
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown("## Profiles")
st.sidebar.markdown(
    """
    [Cosima I](
    https://www.linkedin.com/in/cosima-i-584824264/
    )
    """
)
st.sidebar.markdown(
    """
    [Valentin P](
    https://www.linkedin.com/in/valentin-petitjean-ab1a0324a/
    )
    """)


tab_princing, tab_graphs, tab_quantity = st.tabs(["Pricing", "Graphs", "Quantity"])

with tab_princing :
    st.title("Option Pricer")

    st.header("Market Data")

    col1,col2, col3 = st.columns(3)

    with col1 :
        Spot = st.number_input("Spot ", value=100.0, step=0.01)
        sigma = st.number_input("Volatility ", value =0.2)

    with col2 :
        div = st.number_input("Cash Div ", value = 0.0)
        r = st.number_input("Interest rate ", value=0.030, step=0.001, format="%.3f")
    with col3 :
        date_div = st.date_input("ex-div date ", value =date.today() + timedelta(days=180))
    with col3 :
            pricing_date = st.date_input("Pricing Date ", value =date.today())

    st.header("Option Parameters")

    option_style = st.selectbox(
        "Option Style ",
        ["Vanilla", "Digital (Cash-or-Nothing)", "One Touch"],
    )
    col1,col2,col3 = st.columns(3)

    with col1 :
        K = st.number_input(
            "Barrier" if option_style == "One Touch" else "Strike ",
            value=100.0,
            step=0.01,
            help="The barrier level to be reached for a One Touch option."
            if option_style == "One Touch"
            else None,
        )
    with col2 :
        maturity = st.date_input("Maturity ", value =date.today() + timedelta(days=365))
    with col3:
        option_type = st.selectbox(
            "Barrier Direction" if option_style == "One Touch" else "Option Type ",
            ["CALL", "PUT"],
        )

    st.header("Pricing Method ")
    if option_style == "One Touch":
        is_american = False
        st.info(
            "One Touch options are priced with the trinomial tree and pay the "
            "cash amount when the selected barrier is reached."
        )
        method = st.radio(
            "Choose a pricing method: ",
            ["Trinomial Tree (Backward Method)"],
            horizontal=True,
        )
    elif option_style == "Digital (Cash-or-Nothing)":
        is_american = False
        st.info(
            "Digital options are European and priced with the trinomial tree. "
            "The cash amount is paid at maturity when the option finishes in the money; "
            "at the strike, the payoff is zero."
        )
        method = st.radio(
            "Choose a pricing method: ",
            ["Trinomial Tree (Backward Method)"],
            horizontal=True,
        )
    else :
        exercise_type = st.selectbox("Option Exercice Type ",["European", "American"])
        is_american = (exercise_type == "American")

        if (not is_american and div == 0.0):
            method = st.radio("Choose a pricing method: ",
                            ["Black Scholes","Monte Carlo","Binomial Tree (Backward Method)","Trinomial Tree (Backward Method)"],horizontal=True)
        else :
            method = st.radio("Choose a pricing method: ",
                                ["Trinomial Tree (Backward Method)"],horizontal=True)

        

    np_paths = 0
    if method == "Trinomial Tree (Backward Method)":
        np_paths= st.number_input(
            "Number of Steps ",
            value=50,
            help="American exercise is checked only at tree dates. More steps better capture exercise near the ex-dividend date.",
        )
    
    if method == "Binomial Tree (Backward Method)":
        np_paths= st.number_input("Number of Steps ", value=2)

    if method == "Monte Carlo":
        np_paths= st.number_input("Number of paths ", value=10000)

    tree_method = st.checkbox(
        "Use tree-based spot bump for Delta and Gamma",
        value=True,
        help="When enabled, h = Spot × (alpha - 1). When disabled, h = 2% of Spot.",
    )

    cash = 1.0
    if option_style in ("Digital (Cash-or-Nothing)", "One Touch"):
        cash = st.number_input(
            "Cash payout",
            value=1.0,
            min_value=0.0,
            step=0.1,
        )

    pricing_option_type = option_type
    if option_style == "Digital (Cash-or-Nothing)":
        pricing_option_type = f"DIGITAL_{option_type}"
    elif option_style == "One Touch":
        pricing_option_type = f"ONE_TOUCH_{option_type}"

    #data
    MarketData = Market(Spot,sigma,div,r,pricing_date)
    MarketDataWithDiv = Market(Spot,sigma,div,r,pricing_date,date_div)
    OptionParameters = Option(
        K,
        maturity,
        pricing_option_type,
        is_american,
        cash=cash,
    )
    
    if st.button("Price Option "):
        progress_bar = st.progress(0, text="Calculating price...")

        if (method == "Black Scholes"):
            BSOption = BlackScholes(MarketData,OptionParameters)
            price = BSOption.PricingMethod()
            pricing_results = {"Price": price}

            st.success(f"Option Price with Black Scholes is : {price}")

            MarketValues = (Spot,sigma,div,r,pricing_date)
            progress_bar.progress(0.25, text="Calculating Delta...")
            delta = Delta(BlackScholes,OptionParameters,MarketValues,tree_method=tree_method)
            st.success(f"Option Delta is : {delta}")
            progress_bar.progress(0.5, text="Calculating Gamma...")
            gamma = Gamma(BlackScholes,OptionParameters,MarketValues,tree_method=tree_method)
            st.success(f"Option Gamma is : {gamma}")
            progress_bar.progress(0.75, text="Calculating Vega...")
            vega = Vega(BlackScholes,OptionParameters,MarketValues)
            st.success(f"Option Vega is : {vega}")
            pricing_results.update({"Delta": delta, "Gamma": gamma, "Vega": vega})
            progress_bar.progress(1.0, text="Pricing complete.")

        elif (method == "Monte Carlo"):
                MCOption = MonteCarlo(MarketData,np_paths,OptionParameters)
                price = MCOption.PricingMethod()
                pricing_results = {"Price": price}
        
                st.success(f"Option Price with Monte Carlo is : {price}")

                MarketValues = (Spot,sigma,div,r,pricing_date)
                progress_bar.progress(0.25, text="Calculating Delta...")
                delta = Delta(MonteCarlo,OptionParameters,MarketValues,np_paths,tree_method=tree_method)
                st.success(f"Option Delta is : {delta}")
                progress_bar.progress(0.5, text="Calculating Gamma...")
                gamma = Gamma(MonteCarlo,OptionParameters,MarketValues,np_paths,tree_method=tree_method)
                st.success(f"Option Gamma is : {gamma}")
                progress_bar.progress(0.75, text="Calculating Vega...")
                vega = Vega(MonteCarlo,OptionParameters,MarketValues,np_paths)
                st.success(f"Option Vega is : {vega}")
                pricing_results.update({"Delta": delta, "Gamma": gamma, "Vega": vega})
                progress_bar.progress(1.0, text="Pricing complete.")

        elif (method == "Binomial Tree (Backward Method)"):
                    OptionTree = BinomialTree(MarketData,OptionParameters,np_paths)
                    price = OptionTree.BackwardPricing()
                    pricing_results = {"Price": price}
            
                    st.success(f"Option Price with Binomial Tree is : {price}")

                    MarketValues = (Spot,sigma,div,r,pricing_date)
                    progress_bar.progress(0.25, text="Calculating Delta...")
                    delta = Delta(BinomialTree,OptionParameters,MarketValues,np_paths,tree_method=tree_method)
                    st.success(f"Option Delta is : {delta}")
                    progress_bar.progress(0.5, text="Calculating Gamma...")
                    gamma = Gamma(BinomialTree,OptionParameters,MarketValues,np_paths,tree_method=tree_method)
                    st.success(f"Option Gamma is : {gamma}")
                    progress_bar.progress(0.75, text="Calculating Vega...")
                    vega = Vega(BinomialTree,OptionParameters,MarketValues,np_paths)
                    st.success(f"Option Vega is : {vega}")
                    pricing_results.update({"Delta": delta, "Gamma": gamma, "Vega": vega})
                    progress_bar.progress(1.0, text="Pricing complete.")

        elif (method == "Trinomial Tree (Backward Method)"):
                            OptionTree = TrinomialTree(MarketDataWithDiv,OptionParameters,np_paths)
                            price = OptionTree.BackwardPricing()
                            pricing_results = {"Price": price}
                    
                            st.success(f"Option Price with Trinomial Tree is : {price}")

                            MarketValues = (Spot,sigma,div,r,pricing_date,date_div)
                            progress_bar.progress(0.25, text="Calculating Delta...")
                            delta = Delta(TrinomialTree,OptionParameters,MarketValues,np_paths,tree_method=tree_method)
                            st.success(f"Option Delta is : {delta}")
                            progress_bar.progress(0.5, text="Calculating Gamma...")
                            gamma = Gamma(TrinomialTree,OptionParameters,MarketValues,np_paths,tree_method=tree_method)
                            st.success(f"Option Gamma is : {gamma}")
                            progress_bar.progress(0.75, text="Calculating Vega...")
                            vega = Vega(TrinomialTree,OptionParameters,MarketValues,np_paths)
                            st.success(f"Option Vega is : {vega}")
                            if option_style == "Digital (Cash-or-Nothing)":
                                st.caption(
                                    "Digital-option Greeks can vary with the number of tree steps "
                                    "because the payoff jumps at the strike."
                                )
                            elif option_style == "One Touch":
                                st.caption(
                                    "One Touch Greeks can vary with the number of tree steps "
                                    "because barrier hits are evaluated at tree dates."
                                )
                            pricing_results.update({"Delta": delta, "Gamma": gamma, "Vega": vega})
                            progress_bar.progress(1.0, text="Pricing complete.")

        st.session_state["pricing_results"] = pricing_results


with tab_graphs :

    prices = []
    pricing_times =[]
    
    nb_step= st.number_input("Nb step for convergence",value= 100)
    nb_points = 100
    steps = sorted({round(10 ** (j * log10(nb_step) / (nb_points - 1))) for j in range(nb_points)})

    col1,col2 = st.columns(2)

    st.caption("Charts update automatically with the selected pricing parameters")
    st.caption(f"Current pricing method is : {method}" )
    
    if st.button("Display Graph"):

        if(method =="Binomial Tree (Backward Method)"):
            gc.disable()
            for i in steps:
                if 'OptionTree' in locals():
                    del OptionTree

                start = time.perf_counter()
                OptionTree = BinomialTree(MarketData,OptionParameters,i)
                price = OptionTree.BackwardPricing()
                end = time.perf_counter() -start
            
                prices.append([price,i])
                pricing_times.append(end)

            gc.enable()
            gc.collect()
            BSOption = BlackScholes(MarketData,OptionParameters)
            BSprice = BSOption.PricingMethod()
            
            Graph1 = Convergence(BSprice,prices,pricing_times)
            figure,figure2 = Graph1.Display_graph()
            
            figure3 = Graph1.plot_time_vs_n()
            st.pyplot(figure)
            st.pyplot(figure2)
            st.pyplot(figure3)
        elif(
            method == "Trinomial Tree (Backward Method)"
            and div == 0
            and option_style == "Vanilla"
        ):
            gc.disable()
            for i in steps:
                if 'OptionTree' in locals():
                    del OptionTree

                start = time.perf_counter()
                OptionTree = TrinomialTree(MarketData,OptionParameters,i)
                price = OptionTree.BackwardPricing()
                end = time.perf_counter() -start
            
                prices.append([price,i])
                pricing_times.append(end)

            gc.enable()
            gc.collect()


            BSOption = BlackScholes(MarketData,OptionParameters)
            BSprice = BSOption.PricingMethod()
            
            Graph1 = Convergence(BSprice,prices,pricing_times)
            figure,figure2= Graph1.Display_graph()
       
            figure3 = Graph1.plot_time_vs_n()
            
            st.pyplot(figure)
            st.pyplot(figure2)
            st.pyplot(figure3)

             
        else:
            st.caption("Selected method is not available for charts")
        
        

     
with tab_quantity:
    st.title("Quantity")
    quantity = st.number_input(
        "Quantity",
        value=1.0,
        step=1.0,
        help="Une quantité négative correspond à une position vendeuse.",
    )

    pricing_results = st.session_state.get("pricing_results")
    if pricing_results is None:
        st.info("Calcule d'abord le prix dans l'onglet Pricing.")
    else:
        st.caption(
            "Valeurs du dernier calcul dans Pricing. "
            "Relance le calcul après avoir modifié les paramètres."
        )
        if "Delta" in pricing_results:
            hedge_shares = -pricing_results["Delta"] * quantity
            with st.container(border=True):
                st.subheader("Hedge en actions")
                st.caption(
                    "Position delta-neutre : nombre d'actions à prendre "
                    "pour compenser le Delta de ta position."
                )
                if hedge_shares > 0:
                    st.success("BUY ")
                    st.metric("Quantité d'actions", f"{hedge_shares:,.4f}")
                elif hedge_shares < 0:
                    st.error("SELL")
                    st.metric("Quantité d'actions", f"{abs(hedge_shares):,.4f}")
                else:
                    st.info("Aucune action à acheter ou vendre")
                    st.metric("Quantité d'actions", "0")
                st.caption(
                    f"Calcul : − Delta × quantité d'options "
                    f"(− {pricing_results['Delta']:.6f} × {quantity:g}). "
                    "Convention : 1 option porte sur 1 action."
                )
        else:
            st.info(
                "Le hedge en actions nécessite le Delta. "
                "Il n'est pas disponible pour les options asiatiques."
            )

        st.subheader("Valeur totale de la position")
        for label, value in pricing_results.items():
            st.metric(f"{label} × quantity", f"{value * quantity:.6f}")

     
